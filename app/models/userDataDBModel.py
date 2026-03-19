from sqlalchemy import Column, String
from app.database.database import Base

class UserDataDBModel(Base):
    __tablename__ = "user_data"
    id = Column(String, primary_key=True, index=True)
    userName = Column(String)
    userEmail_id = Column(String, unique=True, index=True)
    userPassword = Column(String)
    userPhoneNumber = Column(String)
    userRole = Column(String)