import json

from app.services.job_description_service import validate_job_description
from app.services.llm_service import enhance_resume


def run_resume_enhancement(resume_text: str, job_description: str, previous_analysis_raw: str) -> dict:
    if not resume_text or not resume_text.strip():
        return {"success": False, "error": "Please upload your resume before requesting improvements."}

    jd_result = validate_job_description(job_description)
    if not jd_result["success"]:
        return {"success": False, "error": jd_result["error"]}

    try:
        previous_analysis = json.loads(previous_analysis_raw) if previous_analysis_raw else None
    except json.JSONDecodeError:
        previous_analysis = None

    if not previous_analysis:
        return {"success": False, "error": "Please run an ATS analysis before requesting resume improvements."}

    return enhance_resume(resume_text, jd_result["text"], previous_analysis)