from pydantic import BaseModel, Field
from typing import Annotated

class UserLogIn(BaseModel):
    userEmail_id : Annotated[str, Field(..., description='Enter your emailId')]
    userPassword : Annotated[str, Field(..., description='Enter your password')]