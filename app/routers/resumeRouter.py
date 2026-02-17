from fastapi import APIRouter, UploadFile, File, Form
from app.resume_parser import extract_text_from_pdf, parse_resume_features
from app.scoring_engine import calculate_ats_score
from app.llm_engine import get_llm_insights

router = APIRouter(prefix='/api/resume', tags=['Resume'])

@router.post("/analyze")
def analyze_resume(resume: UploadFile = File(...), target_role: str = Form(...)):
    print(f"\n--- 🚀 Processing Request for Role: {target_role} ---")
    
    # 1. Extraction (Deterministic)
    file_bytes = resume.file.read()
    print("Reading PDF and extracting features...")
    text = extract_text_from_pdf(file_bytes)
    features = parse_resume_features(text)
    print(f"Detected Skills: {len(features['skills'])}")
    print(f"Detected Projects: {features['projects']}")
    print(f"Detected Experience: {features['experience_years']} years")
    
    # 2. Scoring (Deterministic Logic)
    print("Calculating deterministic base score...")
    det_results = calculate_ats_score(features, target_role)
    print(f"Base Score: {det_results['score']}% | Fit: {det_results['role_fit']}")
    
    # 3. Insights (LLM Semantic Layer) - This provides context that keywords miss
    print("Starting LLM Semantic Analysis (Context & Tips)...")
    insights = get_llm_insights(text, target_role, det_results)
    
    # --- HYBRID REASONING ---
    # Merge deterministic and semantic scores
    semantic_bonus = insights.get("semantic_relevancy_score", 0)
    final_score = det_results["score"] + semantic_bonus
    final_score = max(0, min(100, final_score)) # Hard clamp
    print(f"Semantic Bonus: {semantic_bonus} | Final Adjusted Score: {int(final_score)}%")
    
    # Merge skills (Static DB + LLM found extra)
    all_skills = features["skills"] # Deterministic
    extra_skills = insights.get("extra_skills", [])
    if isinstance(extra_skills, list):
        for s in extra_skills:
            if s.lower() not in [x.lower() for x in all_skills]:
                all_skills.append(s)
    
    # 4. Final Aggregation
    final_result = {
        "score": int(final_score),
        "role_fit": det_results["role_fit"],
        "experience": det_results["experience_level"],
        "projects": features["projects"],
        "skills": sorted(all_skills),
        "missing_skills": det_results["missing_skills"],
        "analysis": insights,
        "job_links": {
            "linkedin_24h": f"https://www.linkedin.com/jobs/search/?keywords={target_role.replace(' ', '+')}&f_TPR=r3600",
            "indeed_24h": f"https://www.indeed.com/jobs?q={target_role.replace(' ', '+')}&fromage=1",
            "naukri": f"https://www.naukri.com/{target_role.replace(' ', '-')}-jobs?freshness=1"
        },
        "debug": {
            "deterministic_score": det_results["score"],
            "semantic_bonus": semantic_bonus
        }
    }
    
    print("--- ✅ Analysis complete ---")
    return final_result