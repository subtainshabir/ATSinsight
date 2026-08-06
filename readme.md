# ATSInsight

AI-powered Resume Analyzer and ATS Checker built with FastAPI, Jinja2, and the Groq API.

Upload a resume, paste a job description, and get a full AI-generated ATS analysis — score, match percentage, strengths, weaknesses, missing keywords/skills, section-by-section evaluation, prioritized improvement recommendations, an AI-rewritten resume, a tailored cover letter, and a downloadable PDF/TXT report.

## Features

- **Resume Upload** — PDF and DOCX, with file type/size/empty validation
- **Text Extraction** — reads resume content while preserving reading order
- **Job Description Input** — with length validation
- **AI Document Validation** — confirms the upload is actually a resume/CV before analyzing it
- **ATS Analysis** — score (0–100), resume match %, summary, strengths, weaknesses, missing keywords/skills, per-section evaluations (experience, education, technical skills, projects, certifications)
- **Score Reasoning** — explains *why* the score is what it is, section by section
- **Prioritized Improvements** — high/medium/low priority recommendations with reasoning, plus an estimated improved score
- **Resume Enhancement** — AI rewrites weak sections (summary, experience, projects, skills) while preserving factual accuracy — never invents experience, skills, or credentials
- **Cover Letter Generator** — tailored to the job description, built only from resume content
- **Export Report** — downloadable PDF (cover page, tables, page numbers, automatic page breaks) or TXT, plus a print-friendly view

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Templates | Jinja2 |
| Styling | Bootstrap 5 + custom CSS |
| AI | Groq API (`groq` Python SDK) |
| PDF text extraction | `pypdf` |
| DOCX text extraction | `python-docx` |
| PDF report generation | `reportlab` |
| Config | `python-dotenv` |

The app is intentionally almost JavaScript-free — nearly every interaction (upload, analyze, improve, generate cover letter, export) is a real HTML form POST handled server-side. The only JavaScript used is for: auto-opening the file picker on upload, copying the cover letter to the clipboard, printing the report, and scrolling to the right section after a page reload.

## Project Structure

```
atsinsight/
├── app/
│   ├── main.py                     # App entrypoint, router registration
│   ├── config/
│   │   └── settings.py             # App settings, .env loading
│   ├── routes/
│   │   ├── upload_routes.py        # POST /upload
│   │   ├── analysis_routes.py      # POST /analyze
│   │   ├── enhancement_routes.py   # POST /improve
│   │   ├── cover_letter_routes.py  # POST /cover-letter
│   │   └── report_routes.py        # POST /export/pdf, POST /export/txt
│   ├── services/
│   │   ├── upload_service.py       # File validation
│   │   ├── pdf_service.py          # PDF text extraction
│   │   ├── docx_service.py         # DOCX text extraction
│   │   ├── extraction_service.py   # Extraction dispatcher
│   │   ├── job_description_service.py  # JD length/empty validation
│   │   ├── analysis_service.py     # Orchestrates ATS analysis
│   │   ├── enhancement_service.py  # Orchestrates resume enhancement
│   │   ├── cover_letter_service.py # Orchestrates cover letter generation
│   │   ├── llm_service.py          # All Groq/AI prompts and calls
│   │   ├── report_service.py       # Report context + TXT report
│   │   └── pdf_report_service.py   # PDF report generation (reportlab)
│   ├── utils/
│   │   └── file_utils.py           # File extension/size helpers
│   ├── templates/
│   │   └── index.html              # Single-page dashboard (Jinja2)
│   └── static/
│       └── css/
│           └── style.css
├── requirements.txt
├── .env                             # Not committed — holds GROQ_API_KEY
└── .env.example
```

## Setup & Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
```

## Environment Variables

Set these in `.env` (see `.env.example`):

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Get a free API key from [console.groq.com](https://console.groq.com).

## Running the App

```bash
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/` in your browser. Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Usage Flow

1. **Upload** a resume (PDF or DOCX).
2. **Paste** a job description (50–10,000 characters).
3. Click **Analyze Resume** — the AI first confirms it's a real resume, then produces the full ATS analysis.
4. Optionally click **Improve Resume** to get an AI-rewritten, more ATS-friendly version.
5. Optionally click **Generate Cover Letter** for a tailored cover letter.
6. Use **Export Report** to download a PDF, download a TXT summary, or print the page.

Since there's no database, all of this state travels between requests via hidden form fields — refreshing with `F5` or navigating away will reset the session, and you'll need to re-upload and re-analyze.

## Known Limitations

- **No persistence** — no database; nothing is saved between sessions.
- **No authentication** — single-user, local use only.
- **AI output isn't guaranteed** — scores, estimates, and rewritten content are AI-generated and should be treated as guidance, not fact. Enhancement and cover letter generation are prompted to never invent experience/skills/credentials, but this is an instructional safeguard, not a hard guarantee.
- **PDF font coverage** — the PDF report currently uses reportlab's default Helvetica font, which doesn't cover every Unicode character (e.g. certain dash/quote characters the AI sometimes outputs can render as `■`). This is a known open issue.
- **Resume Builder module** — not yet implemented; only Resume Analyzer & ATS Checker is complete.

## Not Implemented (Out of Scope So Far)

- Resume Builder
- Database / persistence
- Authentication / multi-user support
- Email sending
- Cloud storage