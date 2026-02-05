from pydantic import BaseModel,Field,EmailStr
from typing import Annotated

class UserInput(BaseModel):
    name: Annotated[str,Field(...,description='Enter your name')]
    email_id : Annotated[EmailStr, Field(..., description='Enter your emailId')]
    