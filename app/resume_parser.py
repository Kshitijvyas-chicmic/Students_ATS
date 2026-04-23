import requests
import json
import os
from dotenv import load_dotenv
from app.core.normalization import normalize_skills_list

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def extract_text_from_pdf(file_bytes):
    import fitz
    """Extract text from PDF bytes directly."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def parse_resume_features(text: str):
    """Extract skills, projects, experience from resume using Groq API."""
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set in environment variables.")

    prompt = f"""
You are an ATS resume parser.

Extract structured information from the resume text below.

Return ONLY valid JSON. Do NOT explain anything. Do NOT add extra text. Do NOT add markdown.
Return strictly in this format:

{{
  "skills": [],
  "experience_years": 0,
  "projects": [
    {{
      "name": "",
      "technologies": []
    }}
  ]
}}

Rules:
1. Extract all technical skills (languages, frameworks, tools, databases) from the **entire resume**, including Skills section, Project descriptions, and Experience section. Only include what is present; do NOT hallucinate.
2. Extract experience_years only if it is **explicitly mentioned** in the resume. If not mentioned, return 0.
3. Extract project names and technologies used in each project as lists.
4. Only return skills, experience_years, and projects. Do NOT add any other info.

Resume Text:
\"\"\"{text}\"\"\"
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")

        raw = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        if not raw:
            raise Exception(f"Groq returned empty response: {response.json()}")

        parsed = json.loads(raw)

        # Normalize skills
        parsed['skills'] = normalize_skills_list(parsed.get('skills', []))

        # Normalize project technologies and merge into skills
        project_skills = set()
        for proj in parsed.get('projects', []):
            proj['technologies'] = normalize_skills_list(proj.get('technologies', []))
            project_skills.update(proj['technologies'])

        # Merge project technologies into skills and remove duplicates
        parsed['skills'] = normalize_skills_list(list(set(parsed['skills']).union(project_skills)))

        return parsed

    except json.JSONDecodeError:
        import re
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("Invalid JSON returned from Groq")

    except Exception as e:
        raise Exception(f"Resume parsing failed: {str(e)}")