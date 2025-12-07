import fitz
import trafilatura
from typing import Optional

def _latin1_safe(s: str) -> str:
    return s.encode('latin-1', 'replace').decode('latin-1')

def compute_ats_analysis(resume_text: str, jd_text: str) -> dict:
    try:
        if not resume_text or not jd_text:
            return {"error": "Resume and Job Description text are required."}
        # Extract keywords (simplified split; extend with NLP later)
        jd_keywords = set(jd_text.lower().split())
        resume_keywords = set(resume_text.lower().split())
        # Calculate keyword match percentage
        matched = len(jd_keywords.intersection(resume_keywords))
        total = len(jd_keywords) if len(jd_keywords) > 0 else 1
        keyword_match = round((matched / total) * 100)
        # Calculate ATS score (weighted by match percentage)
        ats_score = min(round(keyword_match * 1.2), 100)
        # Generate summary
        summary = f"Candidate matches {keyword_match}% of JD keywords. "
        if ats_score >= 80:
            summary += "Strong alignment with job requirements."
        elif ats_score >= 60:
            summary += "Good alignment but missing key terms."
        else:
            summary += "Needs significant optimization for ATS compatibility."
        return {
            "ats_score": f"{ats_score}/100",
            "summary": summary.strip(),
            "keyword_match": f"{keyword_match}%",
            "matched_keywords": list(jd_keywords.intersection(resume_keywords)),
            "missing_keywords": list(jd_keywords.difference(resume_keywords))
        }
    except Exception as e:
        return {"error": f"ATS analysis failed: {type(e).__name__}"}

def compute_resume_optimization(resume_text: str, jd_text: str) -> dict:
    try:
        if not resume_text or not jd_text:
            return {"error": "Resume and Job Description text are required."}
        # Get ATS analysis data for reuse
        ats_data = compute_ats_analysis(resume_text, jd_text)
        if "error" in ats_data:
            return ats_data
        # Simplified skill detection (extend with NLP later)
        technical_skills = set(["python", "fastapi", "sql", "machine learning", "data analysis"])
        soft_skills = set(["communication", "teamwork", "problem solving", "time management"])
        resume_terms = set(resume_text.lower().split())
        missing_technical = list(technical_skills.difference(resume_terms))
        missing_soft = list(soft_skills.difference(resume_terms))
        # Simplified section detection (extend with parsing later)
        sections = {
            "Summary/Objectives": "summary" in resume_text.lower() or "objective" in resume_text.lower(),
            "Experience": "experience" in resume_text.lower() or "work history" in resume_text.lower(),
            "Education": "education" in resume_text.lower(),
            "Skills Section": "skills" in resume_text.lower(),
            "Grammar & Readability": len(resume_text.split()) > 500,
            "Formatting (ATS friendliness)": not any(char in resume_text for char in ["@", "#", "$", "%"])
        }
        # Calculate section ratings (0-10)
        section_ratings = {k: 8 if v else 4 for k, v in sections.items()}
        # Hypothetical updated ATS score after optimization
        updated_ats_score = min(int(ats_data["ats_score"].split("/")[0]) + 15, 100)
        # Suggest achievements (simplified)
        achievement_suggestions = [
            "Add metrics to experience bullet points (e.g., 'Increased efficiency by 20%')",
            "Include specific project outcomes with quantifiable results",
            "Highlight cross-functional collaboration achievements"
        ]
        return {
            "updated_ats_score": f"{updated_ats_score}/100",
            "missing_keywords": ats_data["missing_keywords"],
            "missing_technical_skills": missing_technical,
            "missing_soft_skills": missing_soft,
            "achievement_suggestions": achievement_suggestions,
            "section_ratings": section_ratings,
            "original_ats_data": ats_data
        }
    except Exception as e:
        return {"error": f"Resume optimization failed: {type(e).__name__}"}

def get_ats_resume_templates() -> dict:
    try:
        return {
            "templates": [
                {
                    "id": "template_1",
                    "name": "Minimal ATS-Friendly Resume",
                    "content": "[Name]\n[Phone] | [Email] | [LinkedIn] | [Location]\n\nPROFESSIONAL SUMMARY\n- 2–3 lines tailored to JD with keywords.\n\nSKILLS\n- Skill 1 | Skill 2 | Skill 3 | Skill 4 | Skill 5\n\nWORK EXPERIENCE\nJob Title — Company | Dates\n- Achievement using numbers\n- Responsibility using JD keywords\n- Technology/Tools used\n\nEDUCATION\nDegree — College — Year\n\nPROJECTS\nProject Title\n- Tools used, metrics achieved\n\nCERTIFICATIONS\n- List relevant ones"
                },
                {
                    "id": "template_2",
                    "name": "Metrics-Focused Resume",
                    "content": "[Name]\n[Contact Info]\n\nSUMMARY\n- Short, keyword-rich summary aligned with JD.\n\nCORE SKILLS\n- Categorized technical + soft skills\n\nEXPERIENCE\nCompany — Role — Dates\nKey Achievements:\n- Increased X by Y%\n- Improved Z using A\n- Automated process using B\n\nTOOLS\n- List tools/software exactly matching JD\n\nEDUCATION\n- Degree + Year"
                },
                {
                    "id": "template_3",
                    "name": "Modern Clean Resume (Still ATS Friendly)",
                    "content": "[Name]\n[Phone] | [Email] | [Portfolio]\n\nSUMMARY (One Professional Paragraph)\n\nTECHNICAL SKILLS\n- Grouped by category (Programming, Tools, Frameworks)\n\nPROFESSIONAL EXPERIENCE\nRole | Company | Duration\n- STAR method bullet points\n- Use measurable outcomes\n\nEDUCATION\nDegree | Institute | Year\n\nPROJECTS\n- Bullet points with quantifiable impact"
                }
            ],
            "note": "Templates include placeholders ([...]) for easy customization with your details."}
    except Exception as e:
        return {"error": f"Failed to retrieve ATS templates: {type(e).__name__}"}

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texts = [page.get_text() for page in doc]
        text = "".join(texts).strip()
        return text or "No extractable text found in PDF."
    except Exception:
        return "Invalid or unreadable PDF content."

def scrape_job_description(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "Failed to download job page."
        text = trafilatura.extract(downloaded)
        cleaned = (text or "No text extracted.").strip()[:2500]
        return cleaned or "No text extracted."
    except Exception:
        return "Error scraping job description."

