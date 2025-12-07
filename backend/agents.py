from typing import List, Tuple
from fpdf import FPDF
import re

def _extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#\.\-]+", text)
    freq = {}
    for t in tokens:
        k = t.lower()
        if len(k) < 3:
            continue
        freq[k] = freq.get(k, 0) + 1
    common = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    stop = {"and","the","for","with","that","this","from","into","able","about","your","have","will","are","our","you","job","role","requirements","responsibilities","skills"}
    result = []
    for k, _ in common[:100]:
        if k in stop:
            continue
        result.append(k)
    return result[:25]

def generate_hr_email(applicant_name: str, jd_text: str, resume_text: str) -> str:
    keywords = _extract_keywords(jd_text)
    headline = ", ".join([k.capitalize() for k in keywords[:5]])
    body = (
        f"Dear Hiring Team,\n\n"
        f"I am applying for the opportunity described and believe my background aligns with {headline}. "
        f"My experience includes accomplishments that match your needs. "
        f"I have attached my resume and would welcome the chance to discuss how I can contribute.\n\n"
        f"Thank you for your time and consideration.\n\n"
        f"Best regards,\n{applicant_name}"
    )
    return body

def generate_interview_questions(jd_text: str) -> List[str]:
    keywords = _extract_keywords(jd_text)
    questions = []
    for k in keywords[:10]:
        questions.append(f"How have you applied {k} in a recent project?")
        questions.append(f"What are common pitfalls when working with {k} and how do you avoid them?")
    questions.append("Describe a challenging project and your role end to end.")
    questions.append("How do you prioritize tasks and communicate trade-offs?")
    return questions

def modify_resume(resume_text: str, jd_text: str) -> str:
    keywords = _extract_keywords(jd_text)
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    matched = []
    for kw in keywords:
        for l in lines:
            if kw in l.lower():
                matched.append(l)
    matched = list(dict.fromkeys(matched))
    summary = "Relevant Highlights:\n" + "\n".join(matched[:20]) if matched else "Relevant Highlights:\nTailored summary based on job requirements."
    skills = "Targeted Skills:\n" + ", ".join([k.capitalize() for k in keywords])
    return summary + "\n\n" + skills

def generate_resume_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)
    return pdf.output(dest='S').encode('latin1')
