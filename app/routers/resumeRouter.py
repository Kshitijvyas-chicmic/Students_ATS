from fastapi import APIRouter, UploadFile, File, Form
from app.llm_engine import analyze_resume_with_llm
from app.resume_parser import extract_text_from_pdf

router = APIRouter(prefix='/api/resume', tags=['Resume'])

@router.post("/analyze")
def analyze_resume(resume: UploadFile = File(...), target_role: str = Form(...)):
    print(f"--- Received Request for Role: {target_role} ---")
    # Read file bytes directly using .file.read() to avoid async overhead here
    file_bytes = resume.file.read()
    
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(file_bytes)
    
    print("Running LLM analysis (this might take a minute)...")
    result = analyze_resume_with_llm(text, target_role)
    
    # Add relevant job links
    role_query = target_role.replace(" ", "+")
    result['job_links'] = {
        "linkedin_24h": f"https://www.linkedin.com/jobs/search/?keywords={role_query}&f_TPR=r3600",
        "indeed_24h": f"https://www.indeed.com/jobs?q={role_query}&fromage=1",
        "naukri": f"https://www.naukri.com/{target_role.replace(' ', '-')}-jobs?freshness=1"
    }
    
    print("Analysis complete.")
    return result