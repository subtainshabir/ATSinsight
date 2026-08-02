from fastapi import UploadFile

from app.config.settings import settings
from app.utils.file_utils import get_file_extension, format_file_size


async def process_resume_upload(file: UploadFile) -> dict:
    if not file or file.filename == "":
        return {"success": False, "error": "Please select a resume file to upload."}

    extension = get_file_extension(file.filename)
    if extension not in settings.allowed_resume_extensions:
        return {
            "success": False,
            "error": "Unsupported file type. Please upload a PDF or DOCX file.",
        }

    contents = await file.read()

    if len(contents) == 0:
        return {"success": False, "error": "The uploaded file is empty."}

    max_bytes = settings.max_resume_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        return {
            "success": False,
            "error": f"File is too large. Maximum allowed size is {settings.max_resume_size_mb} MB.",
        }

    return {
        "success": True,
        "filename": file.filename,
        "file_type": extension.replace(".", "").upper(),
        "size_display": format_file_size(len(contents)),
    }