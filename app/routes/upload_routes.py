from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.upload_service import process_resume_upload
from app.services.extraction_service import extract_resume_text

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/upload")
async def upload_resume(request: Request, resume: UploadFile = File(...)):
    upload_result = await process_resume_upload(resume)

    extraction_result = None
    if upload_result["success"]:
        # process_resume_upload already consumed the stream, so rewind
        # before reading the bytes again for extraction.
        await resume.seek(0)
        contents = await resume.read()
        extraction_result = extract_resume_text(contents, upload_result["file_type"])

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "upload_result": upload_result,
            "extraction_result": extraction_result,
        },
    )