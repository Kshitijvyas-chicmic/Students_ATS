from pydantic import BaseModel, Field
from typing import Annotated, List

class InterviewData(BaseModel):
    interviewId: Annotated[str, Field(..., description='Unique identifier for the interview')]
    userId: Annotated[str, Field(..., description='Identifier for the user taking the interview')]
    questions: Annotated[List[str], Field(..., description='List of question IDs included in the interview')]
    score: Annotated[float, Field(..., description='Score achieved in the interview')]
    interviewDate: Annotated[str, Field(..., description='Date when the interview was conducted')]
    interviewStartTime: Annotated[str, Field(..., description='Start time of the interview')]
    interviewEndTime: Annotated[str, Field(..., description='End time of the interview')]
    targetRole: Annotated[str, Field(..., description='The target role for which the interview was conducted')]
    status: Annotated[str, Field(..., description='Status of the interview (e.g., completed, pending, cheated)')]