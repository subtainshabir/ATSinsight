from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.upload_service import process_resume_upload

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/upload")
async def upload_resume(request: Request, resume: UploadFile = File(...)):
    upload_result = await process_resume_upload(resume)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name, "upload_result": upload_result},
    )