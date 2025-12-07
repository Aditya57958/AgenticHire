from typing import Dict, List
from llm import get_llm, llm_generate_hr_email, llm_generate_questions, llm_modify_resume

def run_crewai(applicant_name: str, jd_text: str, resume_text: str, api_key: str | None = None) -> Dict[str, object]:
    llm = get_llm(api_key)
    email = llm_generate_hr_email(llm, applicant_name, jd_text, resume_text)
    questions = llm_generate_questions(llm, jd_text)
    resume = llm_modify_resume(llm, resume_text, jd_text)
    return {"email": email, "questions": questions, "resume": resume}

