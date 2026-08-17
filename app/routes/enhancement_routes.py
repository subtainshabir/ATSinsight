import json

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.enhancement_service import run_resume_enhancement
from app.services import history_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/improve")
async def improve_resume(
    request: Request,
    job_description: str = Form(""),
    resume_text: str = Form(""),
    resume_filename: str = Form(""),
    resume_file_type: str = Form(""),
    resume_size_display: str = Form(""),
    resume_page_count: str = Form(""),
    previous_analysis: str = Form(""),
):
    enhancement_result = run_resume_enhancement(resume_text, job_description, previous_analysis)

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

    ai_result = None
    previous_analysis_json = None
    if previous_analysis.strip():
        try:
            previous_data = json.loads(previous_analysis)
            ai_result = {"success": True, "data": previous_data}
            previous_analysis_json = previous_analysis
        except json.JSONDecodeError:
            ai_result = None

    analysis = {
        "ready": True,
        "resume_error": None,
        "jd_result": {"success": True, "text": job_description},
    }

    enhancement_json = None
    if enhancement_result.get("success"):
        enhancement_json = json.dumps(enhancement_result["data"])

    scroll_target = "enhancement-section" if ai_result else "results-section"

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
            "previous_analysis_json": previous_analysis_json,
            "enhancement_result": enhancement_result,
            "enhancement_json": enhancement_json,
            "scroll_target": scroll_target,
            "history": history_service.get_history(),
        },
    )