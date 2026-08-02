from app.services.job_description_service import validate_job_description


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