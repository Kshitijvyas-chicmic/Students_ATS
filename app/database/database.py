from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Admin@Localhost:5432/student_ATS"

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