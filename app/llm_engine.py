import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _groq_headers():
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set in environment variables.")
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }


def extract_json(text: str):
    if not text:
        return None
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group() if match else None


def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except:
        return None


def normalize_semantic_score(value):
    """
    Normalize -10 to 10 range → convert to -10 to +10 safe int
    """
    try:
        value = int(value)
    except:
        return 0

    return max(min(value, 10), -10)


def get_llm_insights(resume_text: str, target_role: str, deterministic_results: dict):

    truncated_resume = resume_text[:12000]

    prompt = f"""
    Analyze this resume for the role "{target_role}".

    ATS Score: {deterministic_results['score']}%
    Missing Skills: {', '.join(deterministic_results['missing_skills'])}

    Resume:
    {truncated_resume}

    Return ONLY JSON:
    {{
      "summary": "short explanation",
      "improvement_tips": ["tip 1", "tip 2", "tip 3"]
    }}
    """

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    response = requests.post(GROQ_URL, headers=_groq_headers(), json=payload, timeout=30)
    response.raise_for_status()
    raw = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    parsed = safe_json_parse(raw)
    if not parsed:
        raise Exception(f"Groq returned invalid JSON for insights: {raw}")
    return parsed


def generate_interview_questions(target_role: str):
    prompt = f"""
    Generate exactly 10 MCQ questions for a "{target_role}" job interview.
    Each question must have:
    - "question_name": The question text.
    - "options": An array of 4 options.
    - "correct_answer": The exact string match of the correct option.

    Return ONLY JSON matching this structure:
    [
      {{
        "question_name": "What is ...?",
        "options": ["...", "...", "...", "..."],
        "correct_answer": "..."
      }},
      ...
    ]
    """

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.5
    }
    response = requests.post(GROQ_URL, headers=_groq_headers(), json=payload, timeout=30)
    response.raise_for_status()
    raw = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    parsed = json.loads(raw)

    # Handle list or dict wrapped list
    if isinstance(parsed, dict):
        for key in ["questions", "interview_questions", "output"]:
            if key in parsed and isinstance(parsed[key], list):
                parsed = parsed[key]
                break
        else:
            try:
                keys = sorted(parsed.keys(), key=lambda x: int(x) if x.isdigit() else x)
                parsed = [parsed[k] for k in keys if isinstance(parsed[k], dict)]
            except:
                parsed = list(parsed.values())

    if isinstance(parsed, list):
        validated = []
        for q in parsed:
            q_text = q.get("question_name") or q.get("question")
            if q_text and "options" in q:
                validated.append({
                    "question_name": q_text,
                    "options": q["options"],
                    "correct_answer": q.get("correct_answer", "N/A")
                })
        if validated:
            return validated[:10]

    raise Exception(f"Groq returned unexpected structure for interview questions: {raw}")
