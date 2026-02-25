from app.core.skills_db import ROLE_REQUIREMENTS
from app.core.normalization import normalize_skill, normalize_skills_list

def calculate_ats_score(features: dict, target_role: str):
    """
    Skills 60%, Project Tech 25%, Experience 15%.
    Returns ATS score along with breakdown.
    """
    # Role lookup (exact match from dropdown)
    requirements = ROLE_REQUIREMENTS.get(target_role)
    
    if not requirements:
        # Emergency fallback to normalized version or default
        requirements = ROLE_REQUIREMENTS.get(target_role.lower().strip(), 
                                           ROLE_REQUIREMENTS.get("default", {"skills": {}, "min_exp": 1}))

    # Normalize role skill keys
    role_skills = {normalize_skill(k): v for k, v in requirements.get("skills", {}).items()}
    total_skill_points = sum(role_skills.values()) or 1

    # 1. Normalize Resume Skills (Global)
    all_normalized_skills = [normalize_skill(s) for s in features.get("skills", []) if s]
    resume_skills = set(all_normalized_skills)
    
    # 2. Extract and Normalize Project Technologies
    project_tech_list = []
    for proj in features.get("projects", []):
        techs = proj.get("technologies", [])
        project_tech_list.extend([normalize_skill(t) for t in techs if t])
    project_skills = set(project_tech_list)

    # --- 🚩 Keyword Stuffing Penalty (on global skills) ---
    skill_counts = {}
    for s in all_normalized_skills:
        skill_counts[s] = skill_counts.get(s, 0) + 1
    stuffing_penalty = sum((count - 1) * 2 for count in skill_counts.values() if count > 1)

    actual_exp = features.get("experience_years", 0)
    target_exp = requirements.get("min_exp", 1)

    # 1️⃣ Skills Section Score (60%)
    matched_points_skills = 0
    for skill, points in role_skills.items():
        if skill in resume_skills:
            matched_points_skills += points
    skill_section_score = (matched_points_skills / total_skill_points) * 60

    # 2️⃣ Project Technology Score (25%)
    matched_points_projects = 0
    for skill, points in role_skills.items():
        if skill in project_skills:
            matched_points_projects += points
    project_tech_score = (matched_points_projects / total_skill_points) * 25

    # 3️⃣ Identify All Matched Skills (for UI display)
    # A skill is 'Matched' if it exists in either the Skills section OR Project technologies
    found_anywhere = resume_skills.union(project_skills)
    matched_skills_final = [skill for skill in role_skills.keys() if skill in found_anywhere]

    # 4️⃣ Experience Score (15%)
    exp_ratio = min(actual_exp / target_exp, 1)
    exp_score = exp_ratio * 15

    # 5️⃣ Total Score (Apply Penalty)
    base_total = int(round(skill_section_score + project_tech_score + exp_score))
    total_score = max(0, base_total - stuffing_penalty)

    # 6️⃣ Role Fit
    if total_score >= 85:
        role_fit = "Excellent"
    elif total_score >= 70:
        role_fit = "Strong Match"
    elif total_score >= 50:
        role_fit = "Good"
    elif total_score >= 30:
        role_fit = "Average"
    else:
        role_fit = "Poor"

    # ✅ Breakdown
    breakdown = {
        "skill_section_score": round(skill_section_score, 2),
        "project_tech_score": round(project_tech_score, 2),
        "experience_score": round(exp_score, 2),
        "total_skill_points": total_skill_points,
        "matched_skills_count": len(matched_skills_final),
        "experience_years": actual_exp,
        "stuffing_penalty": stuffing_penalty
    }

    return {
        "score": total_score,
        "role_fit": role_fit,
        "matched_skills": sorted(matched_skills_final),
        "missing_skills": sorted(list(set(role_skills.keys()) - found_anywhere)),
        "experience_level": "Fresher" if actual_exp < 1 else "Junior" if actual_exp <= 3 else "Experienced",
        "skill_score": round(skill_section_score, 2), # for backward compatibility
        "project_score": round(project_tech_score, 2),
        "experience_score": round(exp_score, 2),
        "stuffing_penalty": stuffing_penalty,
        "breakdown": breakdown
    }
