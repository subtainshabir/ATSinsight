import uuid
from datetime import datetime
from typing import List, Optional

_history: List[dict] = []


def add_analysis(
    resume_filename: str,
    resume_file_type: str,
    resume_size_display: str,
    resume_page_count: Optional[int],
    resume_text: str,
    job_description: str,
    analysis_data: dict,
) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "filename": resume_filename,
        "file_type": resume_file_type,
        "size_display": resume_size_display,
        "page_count": resume_page_count,
        "resume_text": resume_text,
        "job_description": job_description,
        "created_at": datetime.now().strftime("%b %d, %Y - %I:%M %p"),
        "ats_score": analysis_data.get("ats_score", 0),
        "match_percentage": analysis_data.get("resume_match_percentage", 0),
        "summary": analysis_data.get("resume_summary", ""),
        "data": analysis_data,
    }
    _history.insert(0, record)
    return record


def get_history() -> List[dict]:
    return _history


def get_analysis(analysis_id: str) -> Optional[dict]:
    for record in _history:
        if record["id"] == analysis_id:
            return record
    return None


def delete_analysis(analysis_id: str) -> bool:
    for i, record in enumerate(_history):
        if record["id"] == analysis_id:
            del _history[i]
            return True
    return False


def clear_history() -> None:
    _history.clear()