from app.config.settings import settings


def validate_job_description(job_description: str) -> dict:
    text = (job_description or "").strip()

    if not text:
        return {"success": False, "error": "Job description cannot be empty."}

    if len(text) < settings.min_job_description_length:
        return {
            "success": False,
            "error": f"Job description is too short. Please enter at least "
                     f"{settings.min_job_description_length} characters.",
        }

    if len(text) > settings.max_job_description_length:
        return {
            "success": False,
            "error": f"Job description is too long. Please limit it to "
                     f"{settings.max_job_description_length} characters.",
        }

    return {"success": True, "text": text}