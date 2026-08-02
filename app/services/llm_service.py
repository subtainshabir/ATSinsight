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
]

SYSTEM_PROMPT = """You are an experienced ATS (Applicant Tracking System) engine, a senior technical recruiter, and a career coach combined into one expert reviewer.

Your task has two stages.

STAGE 1 - DOCUMENT VALIDATION
Decide whether the provided document is genuinely a Resume or CV (a document listing a person's work experience, education, skills, or projects for a job application). It is NOT a resume if it is a research paper, assignment, book chapter, invoice, article, notes, or any other non-resume document.

STAGE 2 - ATS ANALYSIS
Only if the document IS a valid resume, compare it against the given Job Description and produce a full ATS analysis.

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
  "overall_recommendation": string (empty string if is_resume is false)
}"""


def _build_user_prompt(resume_text: str, job_description: str) -> str:
    return (
        "Evaluate the following document.\n\n"
        "DOCUMENT TEXT:\n"
        f'"""{resume_text}"""\n\n'
        "JOB DESCRIPTION:\n"
        f'"""{job_description}"""\n\n'
        "Respond with only the JSON object described in your instructions."
    )


def _validate_json_shape(data: dict) -> bool:
    return all(field in data for field in REQUIRED_FIELDS)


def analyze_resume(resume_text: str, job_description: str) -> dict:
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
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(resume_text, job_description)},
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

    if not isinstance(data, dict) or not _validate_json_shape(data):
        return {"success": False, "error": "The AI response was missing expected information. Please try again."}

    return {"success": True, "data": data}