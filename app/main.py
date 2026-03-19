from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.resumeRouter import router as resumeRouter
from app.routers.auth import router as loginRouter
from app.database.database import Base, engine

from app.models.userDataDBModel import UserDataDBModel # Import models so table schemas are registered
app = FastAPI()

Base.metadata.create_all(bind=engine) # create table based on the models defined in the database.py file.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumeRouter)
app.include_router(loginRouter)