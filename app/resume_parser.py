import fitz
import os
import re
from app.core.skills_db import SKILL_DB

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF bytes directly."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_resume_features(text):
    """Deterministic extraction of features from resume text."""
    text_lower = text.lower()
    
    # 1. Extract Skills (Keyword Matching)
    found_skills = set()
    for category in SKILL_DB:
        for skill in SKILL_DB[category]:
            # Use word boundaries to avoid matching "java" in "javascript"
            if re.search(rf"\b{re.escape(skill)}\b", text_lower):
                found_skills.add(skill)
    
    # 2. Estimate Experience (Regex for years)
    exp_years = 0
    # Look for "X years", "X+ years", etc.
    exp_matches = re.findall(r"(\d+)\+?\s*years?[\s\w]*experience", text_lower)
    if exp_matches:
        exp_years = max([int(m) for m in exp_matches])
    
    # 3. Count Projects
    # Look for common project markers: bullet points starting with "Created", "Developed", "Built"
    # Or sections titled "Projects"
    project_count = 0
    if "projects" in text_lower:
        project_section = text_lower.split("projects")[1]
        # Count bullet points or bolded headers (approximate)
        project_count = len(re.findall(r"\n\s*[•\-\*]\s*[A-Z]", text[text_lower.find("projects"):]))
    
    # If regex fails, fallback to a simpler count of links or specific keywords
    if project_count == 0:
        github_links = len(re.findall(r"github\.com", text_lower))
        project_count = max(github_links, 0)

    return {
        "skills": sorted(list(found_skills)),
        "experience_years": exp_years,
        "projects": project_count if project_count > 0 else 1 # Default to 1 if some text exists
    }
