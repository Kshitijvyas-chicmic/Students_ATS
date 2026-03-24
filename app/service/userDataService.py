from fastapi import HTTPException
from app.schema.userData import UserData, TempUserData
from uuid import uuid4
from sqlalchemy.orm import Session
from app.database.userDataDB import register_user as db_register_user
from app.models.userDataDBModel import UserDataDBModel

def register_user(tempUserData: TempUserData, db: Session):
    # Check if user already exists with the same email
    existing_user = db.query(UserDataDBModel).filter(UserDataDBModel.userEmail_id == tempUserData.userEmail_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered. Choose different")

    # Create a new UserData instance with a unique ID
    user_data = UserData(**tempUserData.dict())
    user_data.id = str(uuid4())
    # Save to database
    return db_register_user(userData=user_data, db=db)