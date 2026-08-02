from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
 
load_dotenv()
 
 
class Settings:
    app_name = "ATSInsight"
    app_version = "0.1.0"
    allowed_resume_extensions = {".pdf", ".docx"}
    max_resume_size_mb = 5
    min_job_description_length = 50
    max_job_description_length = 10000
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
 
 
settings = Settings()