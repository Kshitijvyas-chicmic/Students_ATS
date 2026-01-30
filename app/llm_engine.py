from openai import OpenAI
import json

# client = OpenAI()

def analyze_resume_with_llm(resume_text: str):

    prompt = f"""
You are an ATS system.

Analyze the following resume and return ONLY valid JSON.
No explanation. No text outside JSON.

Tasks:
1. Extract technical skills
2. Count number of projects
3. Decide experience level (Fresher / Junior / Experienced)
4. Suggest best role (Backend / Frontend / AI-ML)
5. Give ATS score out of 100
6. Suggest missing skills

Resume:
{resume_text}

Return JSON:
{{
  "skills": [],
  "projects": 0,
  "experience_level": "",
  "best_role": "",
  "score": 0,
  "missing_skills": []
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except:
        return {
            "error": "Invalid JSON from LLM",
            "raw_output": content
        }
