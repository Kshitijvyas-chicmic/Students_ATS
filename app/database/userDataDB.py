from app.schema.userData import UserData
from sqlalchemy.orm import Session
from app.models.userDataDBModel import UserDataDBModel
from app.utils.hashpassword import hash_password

def register_user(userData: UserData, db: Session):
    # Create a new UserDataDBModel instance
    user_data_db = UserDataDBModel(
        id=userData.id,
        userName=userData.userName,
        userEmail_id=userData.userEmail_id,
        userPassword=hash_password(userData.userPassword),
        userPhoneNumber=userData.userPhoneNumber,
        userRole=userData.userRole
    )
    # Add to database and commit
    db.add(user_data_db)
    db.commit()
    db.refresh(user_data_db)
    return "User registered successfully with ID:"+ user_data_db.id