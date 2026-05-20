from fastapi import APIRouter, UploadFile, File, Form, Depends, Request, HTTPException,status
from app.resume_parser import extract_text_from_pdf, parse_resume_features
from app.scoring_engine import calculate_ats_score
from app.llm_engine import get_llm_insights
from app.core.level_skills_DB.fresher import ROLE_REQUIREMENTS
from app.core.normalization import normalize_skills_list
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.utils.jwt import get_current_user


router = APIRouter(prefix='/api/resume', tags=['Resume'])
# APIRouter like a mini fastapi instance that can be included in the main app.

@router.get("/roles")
def get_roles():
    """Get list of available target roles for the dropdown."""
    # Return all keys except 'default'
    roles = [role for role in ROLE_REQUIREMENTS.keys() if role != "default"]
    return sorted(roles)

@router.post("/analyze")
def analyze_resume(request: Request, resume: UploadFile = File(...), target_role: str = Form(...),exp_level: str = Form(...),db: Session = Depends(get_db)):
    current_user = get_current_user(request,db)
    # and the type of current_user is UserDataDBModel
    if current_user.userRole != 'user' and current_user.userRole != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Login page popUP')
    
    print(f"\n--- 🚀 Processing Request for Role: {target_role} ---")
    
    # 1. Extraction (Deterministic)
    file_bytes = resume.file.read()
    print("Reading PDF and extracting features...")

    text = extract_text_from_pdf(file_bytes) # text extract from pdf
    print(text)
    text = text[:12000]

    features = parse_resume_features(text) 
    # type of the features is dict with keys: skills, projects, experience_years
    # and you get everything in normalize form like: everything in lowercase and no extra space
    print("Detected Skills:", features["skills"])
    print("Detected Projects:", features["projects"])
    print("Detected Experience:", features["experience_years"], "years")

    # 2. Scoring (Deterministic Logic)
    print("Calculating deterministic base score...")
    det_results = calculate_ats_score(features, target_role, exp_level)
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
    all_skills = normalize_skills_list(features["skills"]) # Already normalized but for safety
    extra_skills = insights.get("extra_skills", [])
    if isinstance(extra_skills, list):
        all_skills = normalize_skills_list(all_skills + extra_skills)
    
    # 4. Final Aggregation
    final_result = {
        "score": int(final_score),
        "role_fit": det_results["role_fit"],
        "experience": det_results["experience_level"],
        "projects": len(features.get("projects", [])),
        "skills": sorted(all_skills),
        "missing_skills": det_results["missing_skills"],
        "score_breakdown": det_results["breakdown"], # Include the Quantity vs Quality split
        "analysis": insights,
        "job_links": {
            "linkedin_24h": f"https://www.linkedin.com/jobs/search/?keywords={target_role.replace(' ', '+')}&f_TPR=r86400",
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
    