import io
from pypdf import PdfReader


def extract_text_from_pdf(content: bytes) -> dict:
    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception:
        return {"success": False, "error": "The PDF file appears to be corrupted and could not be opened."}

    if len(reader.pages) == 0:
        return {"success": False, "error": "The PDF has no pages."}

    page_texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_texts.append(page_text.strip())

    full_text = "\n\n".join(text for text in page_texts if text)

    if not full_text.strip():
        return {
            "success": False,
            "error": "No readable text found in this PDF. It may be a scanned image.",
        }

    return {"success": True, "text": full_text, "page_count": len(reader.pages)}