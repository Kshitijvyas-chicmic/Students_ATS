import requests
import json
import re

# We will try the base URL first to see if it responds, then use /api/chat
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

def get_llm_insights(resume_text: str, target_role: str, deterministic_results: dict):
    """
    Uses LLM Chat API for semantic analysis. 
    """
    truncated_resume = resume_text[:2500]
    found_skills_str = ", ".join(deterministic_results.get('found_skills', ["None"]))

    prompt = f"""
    Analyze this candidate for "{target_role}".
    SCORE: {deterministic_results['score']}%
    MISSING: {', '.join(deterministic_results['missing_skills'])}
    RESUME: {truncated_resume}

    Return ONLY this JSON:
    {{
      "summary": "1 sentence why they got this score",
      "strengths": ["match 1", "match 2"],
      "improvement_tips": ["tip 1", "tip 2", "tip 3"],
      "soft_skills": ["skill 1", "skill 2", "skill 3"],
      "semantic_relevancy_score": integer -10 to 10,
      "extra_skills": ["skills NOT in: {found_skills_str}"]
    }}
    """

    # Using Chat API (more robust) and simpler model name (llama3.2)
    payload = {
        "model": "llama3.2",
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}
    }

    print(f"--- 🤖 Contacting Ollama at {OLLAMA_CHAT_URL} ---")
    
    try:
        # Check if Ollama is even alive
        requests.get(OLLAMA_BASE, timeout=2)
        
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=90)
        
        if response.status_code == 200:
            result_json = response.json()
            # Chat API returns content inside 'message' -> 'content'
            raw = result_json.get("message", {}).get("content", "")
            
            clean_json = extract_json(raw)
            if clean_json:
                parsed = safe_json_parse(clean_json)
                if parsed:
                    print("--- ✅ AI Chat Analysis Successful ---")
                    return parsed
            print("!! ERROR: Model returned empty content or invalid JSON !!")
            
        elif response.status_code == 404:
            print(f"!! OLLAMA ERROR 404: Endpoint or Model 'llama3.2' not found !!")
            print("Action: Try running 'ollama pull llama3.2' in terminal.")
        else:
            print(f"!! OLLAMA HTTP ERROR: {response.status_code} !!")
            print(f"DEBUG RESPONSE: {response.text[:200]}")

    except Exception as e:
        print(f"!! OLLAMA CONNECTION FAILED: {str(e)} !!")

    print("--- ⚠️ Using Static Fallbacks ---")
    return {
        "summary": f"Your resume has a {deterministic_results['role_fit'].lower()} alignment for {target_role}.",
        "strengths": ["Matched key industry terms", "Experience level detected"],
        "improvement_tips": ["Add more specific project results", "Ensure all 'Must-Have' skills are highlighted", "Use a more industry-standard format"],
        "soft_skills": ["Communication", "Problem Solving", "Professionalism"],
        "semantic_relevancy_score": 0,
        "extra_skills": []
    }
