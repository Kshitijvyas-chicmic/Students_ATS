from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.jwt import get_current_user
from app.llm_engine import generate_interview_questions
from app.models.interviewDataDBModel import InterviewDataDBModel
from datetime import datetime
import uuid

from app.schema.interviewData import InterviewStartRequest, InterviewSubmitRequest

router = APIRouter(prefix="/api/interview", tags=["Interview"])

# Global in-memory cache for questions
interview_cache = {}

@router.post("/start")
def start_interview(payload: InterviewStartRequest, request: Request, db: Session = Depends(get_db)):
    """Auth-protected endpoint to start interview."""
    current_user = get_current_user(request, db)
    
    questions = generate_interview_questions(payload.role)
    interview_id = str(uuid.uuid4())
    
    # Store with correct answers in cache
    interview_cache[interview_id] = {
        "user_id": current_user.id,
        "questions": questions,
        "role": payload.role,
        "start_time": datetime.now()
    }
    
    # Return questions WITHOUT correct answers to frontend
    sanitized_questions = []
    for q in questions:
        if isinstance(q, dict) and "question_name" in q and "options" in q:
            sanitized_questions.append({
                "question_name": q["question_name"],
                "options": q["options"]
            })
    
    return {
        "interview_id": interview_id,
        "questions": sanitized_questions
    }

@router.post("/submit")
def submit_interview(payload: InterviewSubmitRequest, request: Request, db: Session = Depends(get_db)):
    """Submit answers and calculate score."""
    current_user = get_current_user(request, db)
    
    data = interview_cache.get(payload.interview_id)
    if not data:
        print(f"❌ Submission Error: session {payload.interview_id} not found in cache. This usually happens if the server reloaded.")
        raise HTTPException(status_code=400, detail="Session expired due to server reload. Please refresh and try again.")
    
    if data["user_id"] != current_user.id:
        print(f"❌ Submission Error: user mismatch. Cache user: {data['user_id']}, Current user: {current_user.id}")
        raise HTTPException(status_code=400, detail="Invalid session")
    
    correct_questions = data["questions"]
    score = 0
    total = len(correct_questions)
    
    for i, ans in enumerate(payload.user_answers):
        if i < total and ans == correct_questions[i]["correct_answer"]:
            score += 1
    
    final_score = int((score / total) * 100) if total > 0 else 0
    
    # Save to Database
    try:
        interview_entry = InterviewDataDBModel(
            interviewId=payload.interview_id,
            userId=current_user.id,
            score=final_score,
            interviewDate=datetime.now().date(),
            interviewStartTime=data["start_time"].time(),
            interviewEndTime=datetime.now().time(),
            targetRole=data["role"],
            status="completed"
        )
        
        db.add(interview_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Database Error during interview submission: {e}")
        raise HTTPException(status_code=500, detail="Could not save result to database")
    
    # Prepare detailed results for review
    review_data = []
    for i, q in enumerate(correct_questions):
        review_data.append({
            "question": q["question_name"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "user_answer": payload.user_answers[i] if i < len(payload.user_answers) else None,
            "is_correct": i < len(payload.user_answers) and payload.user_answers[i] == q["correct_answer"]
        })

    return {
        "score_out_of_10": round((score / total) * 10, 1) if total > 0 else 0,
        "total_questions": total,
        "correct_count": score,
        "breakdown": review_data
    }
