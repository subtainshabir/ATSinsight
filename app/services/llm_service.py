import json

from groq import (
    Groq,
    AuthenticationError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from app.config.settings import settings

REQUIRED_FIELDS = [
    "is_resume",
    "document_type",
    "validation_message",
    "ats_score",
    "resume_match_percentage",
    "resume_summary",
    "strengths",
    "weaknesses",
    "missing_keywords",
    "missing_skills",
    "experience_evaluation",
    "education_evaluation",
    "technical_skills_evaluation",
    "projects_evaluation",
    "certifications_evaluation",
    "overall_recommendation",
    "ats_score_reason",
    "match_reason",
    "keyword_match_explanation",
    "skills_match_explanation",
    "experience_match_explanation",
    "education_match_explanation",
    "projects_match_explanation",
    "strength_details",
    "weakness_details",
    "high_priority_improvements",
    "medium_priority_improvements",
    "low_priority_improvements",
    "estimated_improved_score",
]

ENHANCEMENT_REQUIRED_FIELDS = [
    "improved_summary",
    "improved_experience",
    "improved_projects",
    "improved_skills",
    "improved_education",
    "improved_certifications",
    "change_log",
    "estimated_new_ats_score",
]

COVER_LETTER_REQUIRED_FIELDS = [
    "cover_letter",
    "key_strengths_used",
    "matched_job_requirements",
]

SYSTEM_PROMPT = """You are an experienced ATS (Applicant Tracking System) engine, a senior technical recruiter, and a career coach combined into one expert reviewer.

Your task has two stages.

STAGE 1 - DOCUMENT VALIDATION
Decide whether the provided document is genuinely a Resume or CV (a document listing a person's work experience, education, skills, or projects for a job application). It is NOT a resume if it is a research paper, assignment, book chapter, invoice, article, notes, or any other non-resume document.

STAGE 2 - ATS ANALYSIS
Only if the document IS a valid resume, compare it against the given Job Description and produce a full ATS analysis. In addition to scoring, you must explain your reasoning and provide a prioritized improvement plan:

- Explain clearly why the ATS score and match percentage came out the way they did, referencing specific resume sections.
- Identify concrete strengths (e.g. strong technical skills, experience, projects, education, certifications, formatting) and explain WHY each one is a strength.
- Identify concrete weaknesses (e.g. missing keywords, weak summary, missing measurable achievements, weak action verbs, missing skills, weak project descriptions, missing certifications, limited experience) and explain WHY each one hurts ATS performance.
- Turn your findings into specific, actionable improvement recommendations, each grouped as high, medium, or low priority, with a short reason for that priority.
- Estimate what the ATS score could realistically become if the high and medium priority recommendations were implemented. This is always an AI estimate, not a guarantee.

Respond with ONLY a single valid JSON object and nothing else - no markdown, no code fences, no text before or after it. The JSON object must always contain exactly these fields:

{
  "is_resume": boolean,
  "document_type": string (e.g. "Resume", "Research Paper", "Invoice", "Article", "Notes", "Other"),
  "validation_message": string (if is_resume is false, briefly explain what the document appears to be instead),
  "ats_score": integer from 0 to 100 (use 0 if is_resume is false),
  "resume_match_percentage": integer from 0 to 100 (use 0 if is_resume is false),
  "resume_summary": string (empty string if is_resume is false),
  "strengths": array of strings (empty array if is_resume is false),
  "weaknesses": array of strings (empty array if is_resume is false),
  "missing_keywords": array of strings (empty array if is_resume is false),
  "missing_skills": array of strings (empty array if is_resume is false),
  "experience_evaluation": string (empty string if is_resume is false),
  "education_evaluation": string (empty string if is_resume is false),
  "technical_skills_evaluation": string (empty string if is_resume is false),
  "projects_evaluation": string (empty string if is_resume is false),
  "certifications_evaluation": string (empty string if is_resume is false),
  "overall_recommendation": string (empty string if is_resume is false),
  "ats_score_reason": string explaining why the ats_score is what it is (empty string if is_resume is false),
  "match_reason": string explaining the overall resume-to-job-description match (empty string if is_resume is false),
  "keyword_match_explanation": string explaining keyword alignment with the job description (empty string if is_resume is false),
  "skills_match_explanation": string explaining skills alignment (empty string if is_resume is false),
  "experience_match_explanation": string explaining experience alignment (empty string if is_resume is false),
  "education_match_explanation": string explaining education alignment (empty string if is_resume is false),
  "projects_match_explanation": string explaining projects alignment (empty string if is_resume is false),
  "strength_details": array of objects like {"title": string, "explanation": string} (empty array if is_resume is false),
  "weakness_details": array of objects like {"title": string, "explanation": string} (empty array if is_resume is false),
  "high_priority_improvements": array of objects like {"recommendation": string, "reason": string} (empty array if is_resume is false),
  "medium_priority_improvements": array of objects like {"recommendation": string, "reason": string} (empty array if is_resume is false),
  "low_priority_improvements": array of objects like {"recommendation": string, "reason": string} (empty array if is_resume is false),
  "estimated_improved_score": integer from 0 to 100 (use 0 if is_resume is false)
}"""

COVER_LETTER_SYSTEM_PROMPT = """You are an expert career coach and professional cover letter writer. You will be given a resume, a job description, a previous ATS analysis of that resume, and optionally an enhanced version of the resume with an improvement change log.

Write a complete, professional cover letter tailored to the job description, using only information found in the resume (or the enhanced resume, if provided). The cover letter must read as a single flowing letter and include, in order:

- A professional greeting (use a specific name only if one is clearly given in the job description, otherwise use a generic professional greeting such as "Dear Hiring Manager,").
- An opening paragraph stating the role being applied for and genuine interest in it.
- A paragraph explaining why the applicant fits the role, referencing the job description.
- A paragraph highlighting relevant experience.
- A paragraph or sentence highlighting relevant skills.
- A paragraph or sentence highlighting relevant projects (only if the resume contains projects).
- A closing paragraph reiterating interest and inviting next steps.
- A professional sign-off (e.g. "Sincerely," followed by the applicant's name if it appears in the resume).

Separate paragraphs with a blank line (\\n\\n) inside the "cover_letter" string. Use confident, natural, professional business language. Keep it concise (roughly 250-400 words).

You MUST NOT invent work experience, employers, job titles, projects, certifications, degrees, technical skills, or achievements that are not present in the resume (or enhanced resume). Do not exaggerate scope, seniority, or impact beyond what is supported by the source material.

Respond with ONLY a single valid JSON object and nothing else - no markdown, no code fences, no text before or after it. The JSON object must always contain exactly these fields:

{
  "cover_letter": string containing the full cover letter with paragraphs separated by blank lines,
  "key_strengths_used": array of strings naming the resume strengths/skills actually referenced in the letter,
  "matched_job_requirements": array of strings naming the job description requirements the letter addresses
}"""

ENHANCEMENT_SYSTEM_PROMPT = """You are an expert resume writer and career coach. You will be given an original resume, a job description, and a previous ATS analysis of that resume (including its score, weaknesses, and missing keywords).

Your job is to rewrite the resume to be more ATS-friendly and better aligned with the job description, while strictly preserving factual accuracy.

You MUST:
- Improve grammar, clarity, and professionalism.
- Strengthen weak action verbs and rewrite weak bullet points.
- Naturally incorporate relevant keywords from the job description and from the previous analysis's missing_keywords/missing_skills, but ONLY where they genuinely fit the person's real background.
- Add measurable language (numbers, scale, impact) only when it can be reasonably inferred from what is already written - never invent specific numbers that are not implied by the original text.
- Only rewrite a section if it actually exists in the original resume. If a section (e.g. certifications) is not present in the original resume, return an empty string or empty array for it and do not add it to change_log.

You MUST NOT, under any circumstances:
- Invent work experience, employers, job titles, projects, certifications, degrees, skills, or achievements that are not present in the original resume.
- Exaggerate scope, seniority, or impact beyond what the original resume supports.

Respond with ONLY a single valid JSON object and nothing else - no markdown, no code fences, no text before or after it. The JSON object must always contain exactly these fields:

{
  "improved_summary": string (empty string if the original resume has no professional summary),
  "improved_experience": array of strings, one improved bullet or entry per item (empty array if no experience section exists),
  "improved_projects": array of strings, one improved bullet or entry per item (empty array if no projects section exists),
  "improved_skills": array of strings (empty array if no skills section exists),
  "improved_education": string with improved wording only, same facts (empty string if no education section exists),
  "improved_certifications": string with improved formatting only, same facts (empty string if no certifications section exists),
  "change_log": array of objects like {"section": string, "before": string, "after": string, "reason": string}, one entry per section that was actually changed. "reason" must explain what changed, why, how it improves ATS compatibility, and which keywords were strengthened or incorporated. Do not include a change_log entry for a section that does not exist in the original resume.,
  "estimated_new_ats_score": integer from 0 to 100, your best estimate of the ATS score after these improvements. This is always an AI estimate, not a guarantee.
}"""
from typing import Optional

def _call_groq_json(system_prompt: str, user_prompt: str) -> dict:
    if not settings.groq_api_key:
        return {
            "success": False,
            "error": "The Groq API key is not configured. Please add GROQ_API_KEY to your .env file.",
        }

    client = Groq(api_key=settings.groq_api_key)

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            timeout=30,
        )
    except AuthenticationError:
        return {"success": False, "error": "The Groq API key is invalid. Please check your .env file."}
    except RateLimitError:
        return {"success": False, "error": "The AI service is currently rate-limited. Please try again shortly."}
    except APITimeoutError:
        return {"success": False, "error": "The AI service took too long to respond. Please try again."}
    except APIConnectionError:
        return {"success": False, "error": "Could not connect to the AI service. Please check your internet connection."}
    except APIStatusError:
        return {"success": False, "error": "The AI service returned an error. Please try again shortly."}
    except Exception:
        return {"success": False, "error": "Something went wrong while contacting the AI service."}

    if not response.choices:
        return {"success": False, "error": "The AI service returned an empty response. Please try again."}

    raw_content = response.choices[0].message.content

    if not raw_content or not raw_content.strip():
        return {"success": False, "error": "The AI service returned an empty response. Please try again."}

    try:
        data = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError):
        return {"success": False, "error": "The AI response could not be understood. Please try again."}

    if not isinstance(data, dict):
        return {"success": False, "error": "The AI response was not in the expected format. Please try again."}

    return {"success": True, "data": data}


def _build_user_prompt(resume_text: str, job_description: str) -> str:
    return (
        "Evaluate the following document.\n\n"
        "DOCUMENT TEXT:\n"
        f'"""{resume_text}"""\n\n'
        "JOB DESCRIPTION:\n"
        f'"""{job_description}"""\n\n'
        "Respond with only the JSON object described in your instructions."
    )


def _build_enhancement_prompt(resume_text: str, job_description: str, previous_analysis: dict) -> str:
    return (
        "Improve the following resume.\n\n"
        "ORIGINAL RESUME TEXT:\n"
        f'"""{resume_text}"""\n\n'
        "JOB DESCRIPTION:\n"
        f'"""{job_description}"""\n\n'
        "PREVIOUS ATS ANALYSIS (for context on what to prioritize):\n"
        f'"""{json.dumps(previous_analysis)}"""\n\n'
        "Respond with only the JSON object described in your instructions."
    )


def _build_cover_letter_prompt(
    resume_text: str,
    job_description: str,
    ats_analysis: dict,
    enhancement_data: Optional[dict],
) -> str:
    enhancement_section = (
        json.dumps(enhancement_data) if enhancement_data else "No resume enhancement has been generated yet."
    )
    return (
        "Write a cover letter based on the following.\n\n"
        "RESUME TEXT:\n"
        f'"""{resume_text}"""\n\n'
        "JOB DESCRIPTION:\n"
        f'"""{job_description}"""\n\n'
        "PREVIOUS ATS ANALYSIS (for context on strongest matches to emphasize):\n"
        f'"""{json.dumps(ats_analysis)}"""\n\n'
        "RESUME ENHANCEMENT (use this improved wording if available, otherwise rely on the resume text above):\n"
        f'"""{enhancement_section}"""\n\n'
        "Respond with only the JSON object described in your instructions."
    )


def _validate_json_shape(data: dict) -> bool:
    return all(field in data for field in REQUIRED_FIELDS)


def _validate_enhancement_shape(data: dict) -> bool:
    return all(field in data for field in ENHANCEMENT_REQUIRED_FIELDS)


def _validate_cover_letter_shape(data: dict) -> bool:
    return all(field in data for field in COVER_LETTER_REQUIRED_FIELDS)


def analyze_resume(resume_text: str, job_description: str) -> dict:
    result = _call_groq_json(SYSTEM_PROMPT, _build_user_prompt(resume_text, job_description))

    if not result["success"]:
        return result

    if not _validate_json_shape(result["data"]):
        return {"success": False, "error": "The AI response was missing expected information. Please try again."}

    return result


def enhance_resume(resume_text: str, job_description: str, previous_analysis: dict) -> dict:
    prompt = _build_enhancement_prompt(resume_text, job_description, previous_analysis)
    result = _call_groq_json(ENHANCEMENT_SYSTEM_PROMPT, prompt)

    if not result["success"]:
        return result

    if not _validate_enhancement_shape(result["data"]):
        return {"success": False, "error": "The AI response was missing expected information. Please try again."}

    return result


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    ats_analysis: dict,
    enhancement_data: Optional[dict],
) -> dict:
    prompt = _build_cover_letter_prompt(resume_text, job_description, ats_analysis, enhancement_data)
    result = _call_groq_json(COVER_LETTER_SYSTEM_PROMPT, prompt)

    if not result["success"]:
        return result

    if not _validate_cover_letter_shape(result["data"]):
        return {"success": False, "error": "The AI response was missing expected information. Please try again."}

    return result