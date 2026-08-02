from app.services.pdf_service import extract_text_from_pdf
from app.services.docx_service import extract_text_from_docx


def extract_resume_text(content: bytes, file_type: str) -> dict:
    try:
        if file_type.upper() == "PDF":
            return extract_text_from_pdf(content)
        elif file_type.upper() == "DOCX":
            return extract_text_from_docx(content)
        return {"success": False, "error": "Unsupported file type for text extraction."}
    except Exception:
        return {"success": False, "error": "The file could not be processed. It may be corrupted."}