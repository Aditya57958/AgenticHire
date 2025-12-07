import base64
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from dotenv import load_dotenv
from utils import extract_text_from_pdf_bytes, scrape_job_description, _latin1_safe, compute_ats_analysis, compute_resume_optimization, get_ats_resume_templates
from agents import generate_hr_email, generate_interview_questions, modify_resume, generate_resume_pdf
from llm import get_llm, llm_generate_hr_email, llm_generate_questions, llm_modify_resume
from crewai_pipeline import run_crewai

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

load_dotenv()
app = FastAPI(title="AgenticHire")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process(step: str = Form(...), resume: Optional[UploadFile] = None, resume_text: Optional[str] = Form(None), job_link: Optional[str] = Form(None), applicant_name: Optional[str] = Form("Applicant"), use_crewai: Optional[str] = Form(None)):
    if step == "ats_analysis":
        if not job_link or (not resume and not resume_text):
            return JSONResponse({"error": "Resume (file or text) and Job Link are required for ATS Analysis step."}, status_code=400)
        if resume:
            pdf_bytes = await resume.read()
            resume_content = extract_text_from_pdf_bytes(pdf_bytes)
        elif resume_text:
            resume_content = resume_text
        jd_text = scrape_job_description(job_link)
        # Run real ATS analysis
        ats_result = compute_ats_analysis(resume_content, jd_text)
        if "error" in ats_result:
            return JSONResponse(ats_result, status_code=400)
        return JSONResponse({
            **ats_result,
            "options": ["Resume Optimization", "Mail for HR"]
        })
    elif step == "resume_optimization":
        if not job_link or (not resume and not resume_text):
            return JSONResponse({"error": "Resume (file or text) and Job Link are required for Resume Optimization step."}, status_code=400)
        if resume:
            pdf_bytes = await resume.read()
            resume_content = extract_text_from_pdf_bytes(pdf_bytes)
        elif resume_text:
            resume_content = resume_text
        jd_text = scrape_job_description(job_link)
        # Run real resume optimization
        optimization_result = compute_resume_optimization(resume_content, jd_text)
        if "error" in optimization_result:
            return JSONResponse(optimization_result, status_code=400)
        return JSONResponse(optimization_result)
    elif step == "ats_templates":
        templates_result = get_ats_resume_templates()
        if "error" in templates_result:
            return JSONResponse(templates_result, status_code=400)
        return JSONResponse(templates_result)
    elif step == "full_process":
        if not job_link or (not resume and not resume_text):
            return JSONResponse({"error": "Resume (file or text) and Job Link are required for Full Process step."}, status_code=400)
        if resume:
            pdf_bytes = await resume.read()
            resume_content = extract_text_from_pdf_bytes(pdf_bytes)
        elif resume_text:
            resume_content = resume_text
        jd_text = scrape_job_description(job_link)
        try:
            if (use_crewai or "").lower() in ("1","true","yes"):
                outputs = run_crewai(applicant_name or "Applicant", jd_text, resume_content)
                email = outputs.get("email") or outputs.get("result") or ""
                questions = outputs.get("questions") or []
                modified_text = outputs.get("resume") or outputs.get("result") or ""
            else:
                llm = get_llm()
                email = llm_generate_hr_email(llm, applicant_name or "Applicant", jd_text, resume_content)
                questions = llm_generate_questions(llm, jd_text)
                modified_text = llm_modify_resume(llm, resume_content, jd_text)
            warning = None
        except Exception as e:
            email = generate_hr_email(applicant_name or "Applicant", jd_text, resume_content)
            questions = generate_interview_questions(jd_text)
            modified_text = modify_resume(resume_content, jd_text)
            warning = f"LLM pipeline failed, used heuristic fallback: {type(e).__name__}"
        pdf_bytes = generate_resume_pdf(_latin1_safe(modified_text))
        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        return JSONResponse({
            "email": email,
            "questions": questions,
            "modified_resume_text": modified_text,
            "modified_resume_pdf_base64": pdf_b64,
            "warning": warning
        })
    else:
        return JSONResponse({"error": "Invalid step provided."}, status_code=400)

