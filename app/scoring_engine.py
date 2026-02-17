from app.core.skills_db import ROLE_REQUIREMENTS

def calculate_ats_score(features, target_role):
    """
    Weighted scoring engine:
    50% - Must-have Skills Match
    20% - Experience Alignment
    15% - Projects Relevance (Bonus)
    15% - Good-to-have Skills (Bonus)
    """
    
    # Normalize target role to find in DB
    role_key = target_role.lower()
    requirements = ROLE_REQUIREMENTS.get("default")
    
    # Try to find a specific role match in the keys
    for key in ROLE_REQUIREMENTS:
        if key in role_key or role_key in key:
            requirements = ROLE_REQUIREMENTS[key]
            break
            
    must_have = set(requirements["must_have"])
    good_to_have = set(requirements["good_to_have"])
    resume_skills = set(features.get("skills", []))
    
    # 1. Skill Score (Must-haves)
    matched_must = must_have.intersection(resume_skills)
    skill_score = (len(matched_must) / len(must_have)) * 50 if must_have else 50
    
    # 2. Experience Score
    target_exp = requirements.get("min_exp", 0)
    actual_exp = features.get("experience_years", 0)
    if target_exp == 0:
        exp_score = 20
    else:
        exp_score = min(actual_exp / target_exp, 1.0) * 20
        
    # 3. Good-to-have Bonus
    matched_good = good_to_have.intersection(resume_skills)
    good_bonus = (len(matched_good) / len(good_to_have)) * 15 if good_to_have else 0
    
    # 4. Project Bonus (Cap at 15 points)
    project_count = features.get("projects", 0)
    project_bonus = min(project_count * 5, 15)
    
    # Calculate Final Score
    total_score = int(skill_score + exp_score + good_bonus + project_bonus)
    total_score = min(total_score, 100) # Clamp to 100
    
    # Determine Role Fit
    if total_score >= 80: role_fit = "Excellent"
    elif total_score >= 60: role_fit = "Good"
    elif total_score >= 40: role_fit = "Average"
    else: role_fit = "Poor"
    
    # Find Missing Skills
    missing_skills = list(must_have - resume_skills)
    
    # Experience Level mapping
    if actual_exp < 1: exp_level = "Fresher"
    elif actual_exp <= 3: exp_level = "Junior"
    else: exp_level = "Experienced"

    return {
        "score": total_score,
        "role_fit": role_fit,
        "missing_skills": missing_skills,
        "experience_level": exp_level,
        "found_skills": list(resume_skills),  # Pass this to LLM
        "analysis_details": {
            "skill_match": len(matched_must),
            "good_match": len(matched_good),
            "exp_actual": actual_exp
        }
    }
