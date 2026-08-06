import json
import logging
import traceback

from fastapi import APIRouter, Request, Form, Response
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.services.report_service import build_report_context, generate_txt_report
from app.services.pdf_report_service import generate_pdf_report

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger("atsinsight.report")


def _rebuild_page_context(
    request: Request,
    job_description: str,
    resume_text: str,
    resume_filename: str,
    resume_file_type: str,
    resume_size_display: str,
    resume_page_count: str,
    previous_analysis: str,
    enhancement_data: str,
    cover_letter_data: str,
    export_error: str = None,
) -> dict:
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
            enhancement_result = {"success": True, "data": json.loads(enhancement_data)}
            enhancement_json = enhancement_data
        except json.JSONDecodeError:
            enhancement_result = None

    cover_letter_result = None
    cover_letter_json = None
    if cover_letter_data.strip():
        try:
            cover_letter_result = {"success": True, "data": json.loads(cover_letter_data)}
            cover_letter_json = cover_letter_data
        except json.JSONDecodeError:
            cover_letter_result = None

    analysis = {
        "ready": True,
        "resume_error": None,
        "jd_result": {"success": True, "text": job_description},
    }

    return {
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
        "export_error": export_error,
        "scroll_target": "results-section",
    }


@router.post("/export/pdf")
async def export_pdf(
    request: Request,
    job_description: str = Form(""),
    resume_text: str = Form(""),
    resume_filename: str = Form(""),
    resume_file_type: str = Form(""),
    resume_size_display: str = Form(""),
    resume_page_count: str = Form(""),
    previous_analysis: str = Form(""),
    enhancement_data: str = Form(""),
    cover_letter_data: str = Form(""),
):
    if not resume_text.strip():
        error = "Please upload your resume before exporting a report."
    elif not previous_analysis.strip():
        error = "Please run an ATS analysis before exporting a report."
    else:
        error = None

    if error:
        context = _rebuild_page_context(
            request, job_description, resume_text, resume_filename, resume_file_type,
            resume_size_display, resume_page_count, previous_analysis, enhancement_data,
            cover_letter_data, export_error=error,
        )
        return templates.TemplateResponse("index.html", context)

    try:
        analysis_data = json.loads(previous_analysis)
        enhancement_json_data = json.loads(enhancement_data) if enhancement_data.strip() else None
        cover_letter_json_data = json.loads(cover_letter_data) if cover_letter_data.strip() else None
        report_context = build_report_context(resume_filename, analysis_data, enhancement_json_data, cover_letter_json_data)
        pdf_bytes = generate_pdf_report(report_context)
    except Exception:
        logger.error("PDF report generation failed:\n%s", traceback.format_exc())
        context = _rebuild_page_context(
            request, job_description, resume_text, resume_filename, resume_file_type,
            resume_size_display, resume_page_count, previous_analysis, enhancement_data,
            cover_letter_data, export_error="We couldn't generate the PDF report. Please try again.",
        )
        return templates.TemplateResponse("index.html", context)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="ATSInsight_Report.pdf"'},
    )


@router.post("/export/txt")
async def export_txt(
    request: Request,
    job_description: str = Form(""),
    resume_text: str = Form(""),
    resume_filename: str = Form(""),
    resume_file_type: str = Form(""),
    resume_size_display: str = Form(""),
    resume_page_count: str = Form(""),
    previous_analysis: str = Form(""),
    enhancement_data: str = Form(""),
    cover_letter_data: str = Form(""),
):
    if not resume_text.strip():
        error = "Please upload your resume before exporting a report."
    elif not previous_analysis.strip():
        error = "Please run an ATS analysis before exporting a report."
    else:
        error = None

    if error:
        context = _rebuild_page_context(
            request, job_description, resume_text, resume_filename, resume_file_type,
            resume_size_display, resume_page_count, previous_analysis, enhancement_data,
            cover_letter_data, export_error=error,
        )
        return templates.TemplateResponse("index.html", context)

    try:
        analysis_data = json.loads(previous_analysis)
        enhancement_json_data = json.loads(enhancement_data) if enhancement_data.strip() else None
        cover_letter_json_data = json.loads(cover_letter_data) if cover_letter_data.strip() else None
        report_context = build_report_context(resume_filename, analysis_data, enhancement_json_data, cover_letter_json_data)
        txt_content = generate_txt_report(report_context)
    except Exception:
        logger.error("TXT report generation failed:\n%s", traceback.format_exc())
        context = _rebuild_page_context(
            request, job_description, resume_text, resume_filename, resume_file_type,
            resume_size_display, resume_page_count, previous_analysis, enhancement_data,
            cover_letter_data, export_error="We couldn't generate the TXT report. Please try again.",
        )
        return templates.TemplateResponse("index.html", context)

    return Response(
        content=txt_content.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="ATSInsight_Analysis.txt"'},
    )