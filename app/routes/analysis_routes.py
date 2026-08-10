import json

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.analysis_service import run_resume_analysis
from app.services import history_service

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
    page_count = int(resume_page_count) if resume_page_count.isdigit() else None

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
            "page_count": page_count,
        }

    previous_analysis_json = None
    if ai_result and ai_result.get("success") and ai_result["data"].get("is_resume"):
        previous_analysis_json = json.dumps(ai_result["data"])
        history_service.add_analysis(
            resume_filename, resume_file_type, resume_size_display, page_count,
            resume_text, job_description, ai_result["data"],
        )

    if analysis.get("resume_error") or (analysis.get("jd_result") and not analysis["jd_result"]["success"]):
        scroll_target = "upload-section"
    else:
        scroll_target = "results-section"

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
            "scroll_target": scroll_target,
            "history": history_service.get_history(),
        },
    )