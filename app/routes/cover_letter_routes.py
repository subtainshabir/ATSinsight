import json

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.cover_letter_service import run_cover_letter_generation
from app.services import history_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/cover-letter")
async def cover_letter(
    request: Request,
    job_description: str = Form(""),
    resume_text: str = Form(""),
    resume_filename: str = Form(""),
    resume_file_type: str = Form(""),
    resume_size_display: str = Form(""),
    resume_page_count: str = Form(""),
    previous_analysis: str = Form(""),
    enhancement_data: str = Form(""),
):
    cover_letter_result = run_cover_letter_generation(
        resume_text, job_description, previous_analysis, enhancement_data
    )

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

    enhancement_result = None
    enhancement_json = None
    if enhancement_data.strip():
        try:
            enhancement_data_parsed = json.loads(enhancement_data)
            enhancement_result = {"success": True, "data": enhancement_data_parsed}
            enhancement_json = enhancement_data
        except json.JSONDecodeError:
            enhancement_result = None

    analysis = {
        "ready": True,
        "resume_error": None,
        "jd_result": {"success": True, "text": job_description},
    }

    cover_letter_json = None
    if cover_letter_result.get("success"):
        cover_letter_json = json.dumps(cover_letter_result["data"])

    scroll_target = "cover-letter-section" if ai_result else "results-section"

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
            "cover_letter_result": cover_letter_result,
            "cover_letter_json": cover_letter_json,
            "scroll_target": scroll_target,
            "history": history_service.get_history(),
        },
    )