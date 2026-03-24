from pydantic import BaseModel, Field
from typing import Annotated
from datetime import date, time


class InterviewData(BaseModel):
    interviewId: Annotated[str, Field(..., description='Unique identifier for the interview')]
    userId: Annotated[str, Field(..., description='Identifier for the user taking the interview')]
    
    score: Annotated[float, Field(..., ge=0, le=100, description='Score achieved in the interview')]
    
    interviewDate: Annotated[date, Field(..., description='Date when the interview was conducted')]
    interviewStartTime: Annotated[time, Field(..., description='Start time of the interview')]
    interviewEndTime: Annotated[time, Field(..., description='End time of the interview')]
    
    targetRole: Annotated[str, Field(..., description='The target role for which the interview was conducted')]
    
    status: Annotated[str, Field(..., description='Status of the interview (completed, pending, cheated)')]