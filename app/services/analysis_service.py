from app.services.job_description_service import validate_job_description
from app.services.llm_service import analyze_resume


def prepare_for_analysis(resume_text: str, job_description: str) -> dict:
    if not resume_text or not resume_text.strip():
        return {
            "ready": False,
            "resume_error": "Please upload your resume before submitting a job description.",
            "jd_result": None,
        }

    jd_result = validate_job_description(job_description)

    return {
        "ready": jd_result["success"],
        "resume_error": None,
        "jd_result": jd_result,
    }


def run_resume_analysis(resume_text: str, job_description: str) -> dict:
    preparation = prepare_for_analysis(resume_text, job_description)

    if not preparation["ready"]:
        return {"preparation": preparation, "ai_result": None}

    ai_result = analyze_resume(resume_text, preparation["jd_result"]["text"])
    return {"preparation": preparation, "ai_result": ai_result}