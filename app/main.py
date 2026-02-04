from fastapi import FastAPI
from app.resume_parser import extract_text_from_pdf
from app.llm_engine import analyze_resume_with_llm

app = FastAPI()

@app.post("/analyze")
def analyze_resume(path: str, target_role: str):
    text = extract_text_from_pdf(path)
    result = analyze_resume_with_llm(text, target_role)
    return result
