from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.analysis_service import run_resume_analysis

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/analyze")
async def analyze(
    request: Request,
    job_description: str = Form(""),
    resume_text: str = Form(""),
    resume_filename: str = Form(""),
    resume_file_type: str = Form(""),
    resume_size_display: str = Form(""),
    resume_page_count: str = Form(""),
):
    result = run_resume_analysis(resume_text, job_description)
    analysis = result["preparation"]
    ai_result = result["ai_result"]

    upload_result = None
    extraction_result = None

    if resume_text.strip():
        upload_result = {
            "success": True,
            "filename": resume_filename,
            "file_type": resume_file_type,
            "size_display": resume_size_display,
        }
        extraction_result = {
            "success": True,
            "text": resume_text,
            "page_count": int(resume_page_count) if resume_page_count.isdigit() else None,
        }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "upload_result": upload_result,
            "extraction_result": extraction_result,
            "job_description": job_description,
            "analysis": analysis,
            "ai_result": ai_result,
        },
    )