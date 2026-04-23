import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
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

    # Prefer Groq if API key is available
    if GROQ_API_KEY:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1 
        }
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                raw = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                parsed = safe_json_parse(raw)
                if parsed:
                    return parsed
        except Exception as e:
            print(f"Groq logic failed, falling back to Ollama: {e}")

    # Fallback to Ollama
    payload = {
        "model": "llama3.2",
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)

        if response.status_code == 200:
            result_json = response.json()
            raw = result_json.get("message", {}).get("content", "")

            clean_json = extract_json(raw)
            if clean_json:
                parsed = safe_json_parse(clean_json)
                if parsed:
                    return parsed

    except Exception:
        pass

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

    # Prefer Groq if API key is available
    if GROQ_API_KEY:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.5
        }
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                raw = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                parsed = json.loads(raw)
                
                # Handle list or dict wrapped list
                if isinstance(parsed, dict):
                    # If Groq returns {"questions": [...]}
                    for key in ["questions", "interview_questions", "output"]:
                        if key in parsed and isinstance(parsed[key], list):
                            parsed = parsed[key]
                            break
                    else:
                        # Fallback: if it's a dict of questions like {"0": {}, "1": {}}
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
        except Exception as e:
            print(f"Groq question generation failed, falling back to Ollama: {e}")

    # Fallback to Ollama
    payload = {
        "model": "llama3.2",
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.5}
    }

    try:
        # Simple health check
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            result_json = response.json()
            raw = result_json.get("message", {}).get("content", "")
            
            # Try to find JSON block - more robust search
            regex = r"(\[[\s\S]*\]|\{[\s\S]*\})"
            match = re.search(regex, raw)
            
            if match:
                data_str = match.group()
                parsed = json.loads(data_str)
                
                # If AI returned a dict with "0", "1"... instead of a list
                if isinstance(parsed, dict):
                    # Sort by key if numeric strings, else just take values
                    try:
                        keys = sorted(parsed.keys(), key=lambda x: int(x))
                        parsed_list = [parsed[k] for k in keys]
                    except:
                        parsed_list = list(parsed.values())
                else:
                    parsed_list = parsed

                # ENSURE it's a list of dicts with keys
                validated = []
                for q in parsed_list:
                    if isinstance(q, dict) and "options" in q:
                        # Fuzzy match key for question
                        q_text = q.get("question_name") or q.get("question")
                        if q_text:
                            validated.append({
                                "question_name": q_text,
                                "options": q["options"],
                                "correct_answer": q.get("correct_answer", "N/A")
                            })
                
                print(f"Validated {len(validated)} questions.")
                return validated[:10]
            else:
                print("No JSON structure found in AI response.")
    except Exception as e:
        print(f"Error generating questions: {e}")
        pass

    # Fallback in case of AI error
    return [
        {
            "question_name": f"Error: Failed to generate questions for {target_role}. Please try again.",
            "options": ["N/A", "N/A", "N/A", "N/A"],
            "correct_answer": "N/A"
        }
    ] * 10
