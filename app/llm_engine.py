import requests
import json
import re

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

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
    Uses LLM for semantic analysis. Includes a retry mechanism for stability.
    """
    # 1. Prepare Primary Attempt
    truncated_resume = resume_text[:2000] # Even shorter for stability
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

    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 400}
    }

    print(f"--- 🤖 Asking AI for semantic insights... ---")
    
    # --- PRIMARY ATTEMPT ---
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            result_json = response.json()
            raw = result_json.get("response", "")
            
            if not raw and "error" in result_json:
                print(f"!! OLLAMA MODEL ERROR: {result_json['error']} !!")
            else:
                clean_json = extract_json(raw)
                if clean_json:
                    parsed = safe_json_parse(clean_json)
                    if parsed:
                        print("--- ✅ AI analysis successful ---")
                        return parsed
        else:
            print(f"!! OLLAMA HTTP ERROR: {response.status_code} !!")
    except Exception as e:
        print(f"!! OLLAMA CONNECTION ERROR: {str(e)} !!")

    # --- RETRY ATTEMPT (SIMPLIFIED) ---
    print("--- 🔄 Retrying with ultra-simple prompt... ---")
    retry_prompt = f"Candidate for {target_role}. Score {deterministic_results['score']}%. Tell me 3 soft skills in JSON format matching the previous schema."
    payload["prompt"] = retry_prompt

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        raw = response.json().get("response", "")
        clean_json = extract_json(raw)
        if clean_json:
            parsed = safe_json_parse(clean_json)
            if parsed:
                print("--- ✅ AI Retry successful (Short Mode) ---")
                # Fill in defaults for missing fields in short mode
                parsed["summary"] = parsed.get("summary") or f"Analysis for {target_role} role."
                return parsed
    except:
        pass

    # --- FINAL FALLBACK (SAFE) ---
    print("--- ⚠️ Using Static Fallbacks ---")
    return {
        "summary": f"Based on keyword matching, your resume shows a {deterministic_results['role_fit'].lower()} fit for {target_role}.",
        "strengths": ["Identified core keywords", "Matches experience patterns"],
        "improvement_tips": ["Incorporate more industry-specific verbs", "Quantify project impact", "Directly address missing skills"],
        "soft_skills": ["Professionalism", "Domain Knowledge", "Adaptability"],
        "semantic_relevancy_score": 0,
        "extra_skills": []
    }
