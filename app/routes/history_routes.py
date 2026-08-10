import json

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services import history_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/history/view/{analysis_id}")
async def view_analysis(request: Request, analysis_id: str):
    record = history_service.get_analysis(analysis_id)

    if not record:
        return RedirectResponse(url="/", status_code=303)

    upload_result = {
        "success": True,
        "filename": record["filename"],
        "file_type": record["file_type"],
        "size_display": record["size_display"],
    }
    extraction_result = {
        "success": True,
        "text": record["resume_text"],
        "page_count": record["page_count"],
    }
    ai_result = {"success": True, "data": record["data"]}
    analysis = {
        "ready": True,
        "resume_error": None,
        "jd_result": {"success": True, "text": record["job_description"]},
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "upload_result": upload_result,
            "extraction_result": extraction_result,
            "job_description": record["job_description"],
            "analysis": analysis,
            "ai_result": ai_result,
            "previous_analysis_json": json.dumps(record["data"]),
            "history": history_service.get_history(),
            "scroll_target": "results-section",
        },
    )


@router.post("/history/delete/{analysis_id}")
async def delete_analysis(analysis_id: str):
    history_service.delete_analysis(analysis_id)
    return RedirectResponse(url="/", status_code=303)


@router.post("/history/clear")
async def clear_history():
    history_service.clear_history()
    return RedirectResponse(url="/", status_code=303)