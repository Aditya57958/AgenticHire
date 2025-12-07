import os
from typing import Optional, List
from langchain_groq import ChatGroq

def get_llm() -> ChatGroq:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("Missing GROQ_API_KEY")
    return ChatGroq(temperature=0.3, model_name="openai/gpt-oss-20b", api_key=key)

def llm_generate_hr_email(llm: ChatGroq, applicant_name: str, jd_text: str, resume_text: str) -> str:
    prompt = (
        "You are an expert HR email writer. Write a concise, professional application email "
        "tailored to the job description. Use the applicant name. Focus on relevance, impact, and clarity. "
        "Highlight 2-3 key skills from the resume that are most relevant to the job description. "
        "Express enthusiasm for the role and the company. Conclude with a call to action, "
        "such as requesting an interview. Keep the email to a maximum of 200 words.\n\n"
        f"Applicant: {applicant_name}\n\nJob Description:\n{jd_text[:4000]}\n\nResume:\n{resume_text[:4000]}\n"
    )
    try:
        out = llm.invoke(prompt)
        return getattr(out, "content", str(out))
    except Exception:
        key = os.getenv("GROQ_API_KEY")
        fallback = ChatGroq(temperature=0.3, model_name="llama-3.1-8b-instant", api_key=key)
        out = fallback.invoke(prompt)
        return getattr(out, "content", str(out))

def llm_generate_questions(llm: ChatGroq, jd_text: str) -> List[str]:
    prompt = (
        "You are an expert interviewer. Generate 10-12 interview questions that are highly relevant to the provided job description. "
        "Include a mix of technical, behavioral, and situational questions. "
        "For each question, consider adding a brief follow-up question to encourage deeper discussion. "
        "Ensure questions cover key skills, experience, and problem-solving abilities. "
        "Return the questions as a numbered list.\n\nJob Description:\n" + jd_text[:5000]
    )
    try:
        out = llm.invoke(prompt)
        text = getattr(out, "content", str(out))
    except Exception:
        key = os.getenv("GROQ_API_KEY")
        fallback = ChatGroq(temperature=0.3, model_name="llama-3.1-8b-instant", api_key=key)
        out = fallback.invoke(prompt)
        text = getattr(out, "content", str(out))
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return lines[:20]

def llm_modify_resume(llm: ChatGroq, resume_text: str, jd_text: str) -> str:
    prompt = (
        "Rewrite and tailor the resume summary and key highlights to align strongly with the job description. "
        "Keep it ATS-friendly and emphasize measurable impact. Return plain text sections: 'Summary', 'Highlights', 'Skills'.\n\n"
        f"Job Description:\n{jd_text[:5000]}\n\nResume:\n{resume_text[:5000]}\n"
    )
    try:
        out = llm.invoke(prompt)
        return getattr(out, "content", str(out))
    except Exception:
        key = os.getenv("GROQ_API_KEY")
        fallback = ChatGroq(temperature=0.3, model_name="llama-3.1-8b-instant", api_key=key)
        out = fallback.invoke(prompt)
        return getattr(out, "content", str(out))
