from app.schema.userData import UserData, TempUserData
from uuid import uuid4
from sqlalchemy.orm import Session
from app.database.userDataDB import register_user

def register_user(tempUserData: TempUserData, db: Session):
    # Create a new UserData instance with a unique ID
    user_data = UserData(**tempUserData.dict())
    user_data.id = str(uuid4())
    # Save to database
    return register_user(userData=user_data, db=db)