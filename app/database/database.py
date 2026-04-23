import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Check environment variable first (for Render), fallback to local
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Admin@localhost:5432/student_ATS")

# Fix for Render's 'postgres://' quirk
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
# This engine work is connect to the database

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# This sessionLocal is a factory for creating new Session object when we need to interact with the db

Base = declarative_base()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()