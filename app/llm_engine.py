import requests
import json
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group() if match else None


def safe_json_parse(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from LLM", "raw": text}


def analyze_resume_with_llm(resume_text: str, target_role: str):

    # Truncate to 12,000 chars to ensure we read the entire resume (Experience/Projects are often at the end)
    # Llama 3.2 can handle this context easily.
    truncated_resume = resume_text[:12000]

    prompt = f"""
    You are a Professional ATS (Applicant Tracking System) Engine.
    Your output MUST be a single, valid JSON object. No markdown. No text outside the JSON.

    TARGET ROLE: "{target_role}"

    RESUME CONTENT:
    {truncated_resume}

    ### CORE RULES:
    1. **SKILLS**: Extract EVERY single technical skill, tool, and framework from the resume text. 
       - **DO NOT FILTER**. If it's on the resume, list it in the "skills" array.
    2. **PROJECTS**: Count only distinct, named technical projects.
    3. **EXPERIENCE**: 
       - Calculate total years of professional work experience.
       - < 1 yr: "Fresher" | 1-3 yrs: "Junior" | 3+ yrs: "Experienced".
    4. **SCORING**:
       - 80-95: Strong match (Candidate has core skills like {target_role}).
       - 40-79: Average match (Some skills match, but not the primary stack).
       - 0-39: Poor match (Ecosystem mismatch or irrelevant resume).
    5. **MISSING SKILLS**: List critical skills for "{target_role}" that are NOT present in the resume.

    ### STRICT JSON FORMAT:
    {{
      "skills": [],
      "projects": 0,
      "experience_level": "",
      "role_fit": "Poor" | "Average" | "Good" | "Excellent",
      "score": 0,
      "missing_skills": []
    }}
    """

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    print(f"--- Sending Prompt to Ollama ({payload['model']}) ---")
    try:
        # High timeout for CPU
        response = requests.post(OLLAMA_URL, json=payload, timeout=600)
        print("--- Received Response from Ollama ---")
        raw = response.json().get("response", "")
    except requests.exceptions.ConnectionError:
        print("!! OLLAMA CONNECTION FAILED - RETURNING MOCK DATA !!")
        return {
            "skills": ["MOCK_SKILL_1", "MOCK_SKILL_2", "Java (Mock)", "Python (Mock)"],
            "projects": 99,
            "experience_level": "Mock Data (Ollama Down)",
            "role_fit": "Poor",
            "score": 10,
            "missing_skills": ["Ollama Service Not Running", "Please Start Ollama"],
            "warning": "⚠️ server could not connect to Ollama. This is dummy data."
        }
    except Exception as e:
        return {"error": f"LLM Error: {str(e)}"}

    clean_json = extract_json(raw)
    if not clean_json:
        return {"error": "No JSON from LLM", "raw": raw}

    data = safe_json_parse(clean_json)

    # 🔒 HARD SAFETY CLAMP (in case model still lies)
    if "role_fit" in data and "score" in data:
        rf = data.get("role_fit")
        # Handle cases where score might be a string or missing
        try:
            sc = int(data.get("score", 0))
        except:
            sc = 0

        if rf == "Good":
            data["score"] = max(70, min(95, sc))
        elif rf == "Average":
            data["score"] = max(40, min(69, sc))
        elif rf == "Poor":
            data["score"] = max(0, min(39, sc))

    return data
