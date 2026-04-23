from pydantic import BaseModel,Field,EmailStr
from typing import Annotated

class TempUserData(BaseModel):
    userName: Annotated[str,Field(...,description='Enter your name')]
    userEmail_id : Annotated[EmailStr, Field(..., description='Enter your emailId')]
    userPassword : Annotated[str, Field(..., description='Enter your password')]
    userPhoneNumber : Annotated[str, Field(..., description='Enter your phone number')]

class UserData(TempUserData):
    # Set the role by default to "user" for all registered users
    id: str = "None"
    userRole: str = "user"