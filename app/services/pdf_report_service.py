import hashlib
import io
from xml.sax.saxutils import escape

_original_md5 = hashlib.md5
try:
    _original_md5(usedforsecurity=False)
except TypeError:
    def _md5_compat(*args, **kwargs):
        kwargs.pop("usedforsecurity", None)
        return _original_md5(*args, **kwargs)
    hashlib.md5 = _md5_compat

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)

INK = colors.HexColor("#12172B")
INK_SOFT = colors.HexColor("#565C74")
ACCENT = colors.HexColor("#F2A93B")
LINE = colors.HexColor("#E3E5EA")
PAPER = colors.HexColor("#F6F7F5")


class _NumberedCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            if total_pages > 1:
                self._draw_footer(total_pages)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_footer(self, total_pages):
        self.setFont("Helvetica", 8)
        self.setFillColor(INK_SOFT)
        self.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"Page {self._pageNumber} of {total_pages}")
        self.drawString(0.75 * inch, 0.5 * inch, "ATSInsight")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportHeading", parent=styles["Heading1"], textColor=INK, fontSize=15, spaceBefore=18, spaceAfter=8))
    styles.add(ParagraphStyle(name="ReportSubheading", parent=styles["Heading2"], textColor=INK, fontSize=11.5, spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle(name="ReportBody", parent=styles["Normal"], textColor=INK, fontSize=9.5, leading=14))
    styles.add(ParagraphStyle(name="ReportMuted", parent=styles["Normal"], textColor=INK_SOFT, fontSize=9.5, leading=14))
    return styles


def _esc(value) -> str:
    """Escape dynamic (AI-generated or user-provided) text before it goes into a Paragraph."""
    if value is None or value == "":
        return ""
    return escape(str(value))


def _markup(text: str, style):
    """Wrap already-safe markup (static labels, or text built with _esc()) in a Paragraph."""
    return Paragraph(text if text else "&nbsp;", style)


def _body(text, style):
    """Wrap raw dynamic text in a Paragraph, escaping it first."""
    escaped = _esc(text)
    return Paragraph(escaped if escaped else "&nbsp;", style)


def _bullets(items, styles, empty_text="No items identified."):
    if not items:
        return [_markup(empty_text, styles["ReportMuted"])]
    return [_markup(f"&bull; {_esc(item)}", styles["ReportBody"]) for item in items]


def _detail_bullets(items, styles, title_key, reason_key, empty_text="No items identified."):
    if not items:
        return [_markup(empty_text, styles["ReportMuted"])]
    flowables = []
    for item in items:
        if isinstance(item, dict):
            title = item.get(title_key, "")
            reason = item.get(reason_key, "")
        else:
            title = item
            reason = ""
        flowables.append(_markup(f"&bull; <b>{_esc(title)}</b>", styles["ReportBody"]))
        if reason:
            flowables.append(_body(reason, styles["ReportMuted"]))
        flowables.append(Spacer(1, 4))
    return flowables


def generate_pdf_report(context: dict) -> bytes:
    a = context["analysis"] or {}
    styles = _styles()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        title="ATSInsight Report",
    )

    story = []

    story.append(Spacer(1, 1.6 * inch))
    logo_table = Table([["ATSInsight"]], colWidths=[2.2 * inch])
    logo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(logo_table)
    story.append(Spacer(1, 0.3 * inch))
    story.append(_markup("AI Resume Analyzer &amp; ATS Checker", styles["ReportMuted"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(_markup("ATS Analysis Report", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(_body(f"Resume: {context['resume_filename']}", styles["ReportBody"]))
    story.append(_body(f"Generated: {context['generated_at']}", styles["ReportMuted"]))
    story.append(PageBreak())

    story.append(_markup("ATS Score &amp; Match", styles["ReportHeading"]))
    score_table = Table(
        [["ATS Score", f"{a.get('ats_score', '')}/100"], ["Resume Match", f"{a.get('resume_match_percentage', '')}%"]],
        colWidths=[2 * inch, 2 * inch],
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PAPER),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)

    story.append(_markup("Resume Summary", styles["ReportSubheading"]))
    story.append(_body(a.get("resume_summary", ""), styles["ReportBody"]))

    story.append(_markup("Why This Score", styles["ReportSubheading"]))
    story.append(_body(a.get("ats_score_reason", ""), styles["ReportBody"]))

    story.append(_markup("Resume Strengths", styles["ReportSubheading"]))
    story.extend(_detail_bullets(a.get("strength_details", []), styles, "title", "explanation"))

    story.append(_markup("Resume Weaknesses", styles["ReportSubheading"]))
    story.extend(_detail_bullets(a.get("weakness_details", []), styles, "title", "explanation"))

    story.append(_markup("Missing Keywords", styles["ReportSubheading"]))
    story.extend(_bullets(a.get("missing_keywords", []), styles))

    story.append(_markup("Missing Skills", styles["ReportSubheading"]))
    story.extend(_bullets(a.get("missing_skills", []), styles))

    for label, key in [
        ("Experience Evaluation", "experience_evaluation"),
        ("Education Evaluation", "education_evaluation"),
        ("Technical Skills Evaluation", "technical_skills_evaluation"),
        ("Projects Evaluation", "projects_evaluation"),
        ("Certifications Evaluation", "certifications_evaluation"),
    ]:
        story.append(_markup(label, styles["ReportSubheading"]))
        story.append(_body(a.get(key, ""), styles["ReportBody"]))

    story.append(_markup("High Priority Improvements", styles["ReportSubheading"]))
    story.extend(_detail_bullets(a.get("high_priority_improvements", []), styles, "recommendation", "reason"))

    story.append(_markup("Medium Priority Improvements", styles["ReportSubheading"]))
    story.extend(_detail_bullets(a.get("medium_priority_improvements", []), styles, "recommendation", "reason"))

    story.append(_markup("Low Priority Improvements", styles["ReportSubheading"]))
    story.extend(_detail_bullets(a.get("low_priority_improvements", []), styles, "recommendation", "reason"))

    story.append(_markup("Estimated Improved ATS Score", styles["ReportSubheading"]))
    story.append(_markup(
        f"Current: {_esc(a.get('ats_score', ''))}  &#8594;  Estimated: {_esc(a.get('estimated_improved_score', ''))} (AI estimate)",
        styles["ReportBody"],
    ))

    story.append(_markup("Overall Recommendation", styles["ReportSubheading"]))
    story.append(_body(a.get("overall_recommendation", ""), styles["ReportBody"]))

    if context["enhancement"] and isinstance(context["enhancement"], dict):
        e = context["enhancement"]
        story.append(PageBreak())
        story.append(_markup("Resume Enhancement", styles["ReportHeading"]))

        if e.get("improved_summary"):
            story.append(_markup("Improved Professional Summary", styles["ReportSubheading"]))
            story.append(_body(e["improved_summary"], styles["ReportBody"]))

        if e.get("improved_experience"):
            story.append(_markup("Improved Experience", styles["ReportSubheading"]))
            story.extend(_bullets(e["improved_experience"], styles))

        if e.get("improved_projects"):
            story.append(_markup("Improved Projects", styles["ReportSubheading"]))
            story.extend(_bullets(e["improved_projects"], styles))

        if e.get("improved_skills"):
            story.append(_markup("Improved Skills", styles["ReportSubheading"]))
            story.extend(_bullets(e["improved_skills"], styles))

        story.append(_markup("Improvement Summary", styles["ReportSubheading"]))
        story.append(_markup(
            f"Estimated New ATS Score: {_esc(e.get('estimated_new_ats_score', ''))} (AI estimate)",
            styles["ReportBody"],
        ))
        change_items = []
        for c in e.get("change_log", []):
            if isinstance(c, dict):
                change_items.append({"title": c.get("section", ""), "explanation": c.get("reason", "")})
            else:
                change_items.append({"title": str(c), "explanation": ""})
        story.extend(_detail_bullets(change_items, styles, "title", "explanation"))

    if context["cover_letter"] and isinstance(context["cover_letter"], dict):
        c = context["cover_letter"]
        story.append(PageBreak())
        story.append(_markup("Cover Letter", styles["ReportHeading"]))
        for paragraph in c.get("cover_letter", "").split("\n\n"):
            if paragraph.strip():
                story.append(_body(paragraph.strip(), styles["ReportBody"]))
                story.append(Spacer(1, 8))

    doc.build(story, canvasmaker=_NumberedCanvas)
    return buffer.getvalue()