from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.resumeRouter import router as resumeRouter
from app.routers.auth import router as loginRouter
from app.routers.interviewRouter import router as interviewRouter
from app.database.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os

from app.models.userDataDBModel import UserDataDBModel # Import models so table schemas are registered
from app.models.interviewDataDBModel import InterviewDataDBModel
app = FastAPI()

Base.metadata.create_all(bind=engine) # create table based on the models defined in the database.py file.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://student-ats.vercel.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumeRouter)
app.include_router(loginRouter)
app.include_router(interviewRouter)

# Serve static files from the 'frontend' directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")