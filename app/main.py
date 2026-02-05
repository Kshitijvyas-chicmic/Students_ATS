from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.resumeRouter import router as resumeRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumeRouter)
