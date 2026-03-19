import requests
import json
from app.core.normalization import normalize_skills_list

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest"  # change if using other models


def normalize_text(text: str) -> str:
    """Normalize text safely: lowercase, strip, collapse spaces."""
    return re.sub(r"\s+", " ", text.lower().strip())


def extract_text_from_pdf(file_bytes):
    import fitz
    """Extract text from PDF bytes directly."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def parse_resume_features(text: str):
    """Extract skills, projects, experience from resume and normalize everything."""
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

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "format": "json",
                "stream": False
            },
            timeout=180
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        data = response.json()
        result = data.get("response", "")
        if not result:
            raise Exception(f"Unexpected Ollama response: {data}")

        parsed = json.loads(result)

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
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("Invalid JSON returned from Ollama")

    except requests.exceptions.ConnectionError:
        raise Exception("Ollama server is not running. Please start Ollama on your machine (http://localhost:11434).")
    except Exception as e:
        raise Exception(f"Resume parsing failed: {str(e)}")