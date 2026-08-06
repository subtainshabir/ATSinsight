from datetime import datetime


def build_report_context(resume_filename: str, analysis_data: dict, enhancement_data: dict, cover_letter_data: dict) -> dict:
    return {
        "generated_at": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "resume_filename": resume_filename or "Uploaded Resume",
        "analysis": analysis_data,
        "enhancement": enhancement_data,
        "cover_letter": cover_letter_data,
    }


def _lines_for_pairs(pairs: list) -> list:
    return [f"{label}: {value}" for label, value in pairs]


def _lines_for_bullets(items: list) -> list:
    return [f"  - {item}" for item in items] if items else ["  (none identified)"]


def _lines_for_detail_items(items: list) -> list:
    lines = []
    for item in items:
        lines.append(f"  - {item.get('title', item.get('recommendation', ''))}")
        reason = item.get("explanation", item.get("reason", ""))
        if reason:
            lines.append(f"    {reason}")
    return lines if items else ["  (none identified)"]


def generate_txt_report(context: dict) -> str:
    a = context["analysis"] or {}
    lines = []

    lines.append("ATSInsight - ATS Analysis Report")
    lines.append(f"Generated: {context['generated_at']}")
    lines.append(f"Resume: {context['resume_filename']}")
    lines.append("=" * 60)

    lines.append("")
    lines.append("ATS SCORE & MATCH")
    lines.append("-" * 60)
    lines.extend(_lines_for_pairs([
        ("ATS Score", f"{a.get('ats_score', '')}/100"),
        ("Resume Match", f"{a.get('resume_match_percentage', '')}%"),
    ]))

    lines.append("")
    lines.append("RESUME SUMMARY")
    lines.append("-" * 60)
    lines.append(a.get("resume_summary", ""))

    lines.append("")
    lines.append("WHY THIS SCORE")
    lines.append("-" * 60)
    lines.append(a.get("ats_score_reason", ""))

    lines.append("")
    lines.append("RESUME STRENGTHS")
    lines.append("-" * 60)
    lines.extend(_lines_for_detail_items(a.get("strength_details", [])))

    lines.append("")
    lines.append("RESUME WEAKNESSES")
    lines.append("-" * 60)
    lines.extend(_lines_for_detail_items(a.get("weakness_details", [])))

    lines.append("")
    lines.append("MISSING KEYWORDS")
    lines.append("-" * 60)
    lines.extend(_lines_for_bullets(a.get("missing_keywords", [])))

    lines.append("")
    lines.append("MISSING SKILLS")
    lines.append("-" * 60)
    lines.extend(_lines_for_bullets(a.get("missing_skills", [])))

    lines.append("")
    lines.append("SECTION EVALUATIONS")
    lines.append("-" * 60)
    lines.extend(_lines_for_pairs([
        ("Experience", a.get("experience_evaluation", "")),
        ("Education", a.get("education_evaluation", "")),
        ("Technical Skills", a.get("technical_skills_evaluation", "")),
        ("Projects", a.get("projects_evaluation", "")),
        ("Certifications", a.get("certifications_evaluation", "")),
    ]))

    lines.append("")
    lines.append("HIGH PRIORITY IMPROVEMENTS")
    lines.append("-" * 60)
    lines.extend(_lines_for_detail_items(a.get("high_priority_improvements", [])))

    lines.append("")
    lines.append("MEDIUM PRIORITY IMPROVEMENTS")
    lines.append("-" * 60)
    lines.extend(_lines_for_detail_items(a.get("medium_priority_improvements", [])))

    lines.append("")
    lines.append("LOW PRIORITY IMPROVEMENTS")
    lines.append("-" * 60)
    lines.extend(_lines_for_detail_items(a.get("low_priority_improvements", [])))

    lines.append("")
    lines.append("ESTIMATED IMPROVED ATS SCORE")
    lines.append("-" * 60)
    lines.append(f"Current: {a.get('ats_score', '')}  ->  Estimated: {a.get('estimated_improved_score', '')} (AI estimate)")

    lines.append("")
    lines.append("OVERALL RECOMMENDATION")
    lines.append("-" * 60)
    lines.append(a.get("overall_recommendation", ""))

    if context["enhancement"]:
        e = context["enhancement"]
        lines.append("")
        lines.append("=" * 60)
        lines.append("RESUME ENHANCEMENT")
        lines.append("=" * 60)

        if e.get("improved_summary"):
            lines.append("")
            lines.append("Improved Professional Summary")
            lines.append("-" * 60)
            lines.append(e["improved_summary"])

        if e.get("improved_experience"):
            lines.append("")
            lines.append("Improved Experience")
            lines.append("-" * 60)
            lines.extend(_lines_for_bullets(e["improved_experience"]))

        if e.get("improved_projects"):
            lines.append("")
            lines.append("Improved Projects")
            lines.append("-" * 60)
            lines.extend(_lines_for_bullets(e["improved_projects"]))

        if e.get("improved_skills"):
            lines.append("")
            lines.append("Improved Skills")
            lines.append("-" * 60)
            lines.extend(_lines_for_bullets(e["improved_skills"]))

        lines.append("")
        lines.append("Improvement Summary")
        lines.append("-" * 60)
        lines.append(f"Estimated New ATS Score: {e.get('estimated_new_ats_score', '')} (AI estimate)")
        for change in e.get("change_log", []):
            lines.append(f"  - {change.get('section', '')}: {change.get('reason', '')}")

    if context["cover_letter"]:
        c = context["cover_letter"]
        lines.append("")
        lines.append("=" * 60)
        lines.append("COVER LETTER")
        lines.append("=" * 60)
        lines.append("")
        lines.append(c.get("cover_letter", ""))

    return "\n".join(lines)