import requests
import json
import re

OLLAMA_BASE = "http://127.0.0.1:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"


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

    truncated_resume = resume_text[:2500]

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

    # keep your existing Ollama call logic


    payload = {
        "model": "llama3.2",
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        requests.get(OLLAMA_BASE, timeout=2)

        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=90)

        if response.status_code == 200:
            result_json = response.json()
            raw = result_json.get("message", {}).get("content", "")

            clean_json = extract_json(raw)
            if clean_json:
                parsed = safe_json_parse(clean_json)
                if parsed:
                    parsed["semantic_relevancy_score"] = normalize_semantic_score(
                        parsed.get("semantic_relevancy_score", 0)
                    )
                    return parsed

    except Exception:
        pass

    # fallback
    return {
        "summary": f"Resume has {deterministic_results['role_fit']} alignment for {target_role}.",
        "improvement_tips": [],
        "semantic_relevancy_score": 0
    }
