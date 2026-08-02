from pydantic_settings import BaseSettings

class Settings:
    app_name = "ATSInsight"
    app_version = "0.1.0"
    allowed_resume_extensions = {".pdf", ".docx"}
    max_resume_size_mb = 5
    min_job_description_length = 50
    max_job_description_length = 10000


settings = Settings()