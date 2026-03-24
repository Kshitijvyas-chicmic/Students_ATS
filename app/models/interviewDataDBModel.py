from sqlalchemy import Column, String, Float, Date, Time, ForeignKey
from app.database.database import Base


class InterviewDataDBModel(Base):
    __tablename__ = "interview_data"

    interviewId = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user_data.id"), nullable=False, index=True)

    score = Column(Float, nullable=False)

    interviewDate = Column(Date, nullable=False)
    interviewStartTime = Column(Time, nullable=False)
    interviewEndTime = Column(Time, nullable=False)

    targetRole = Column(String, nullable=False)

    status = Column(String, nullable=False)