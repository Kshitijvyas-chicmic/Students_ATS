from pydantic import BaseModel , Field
from typing import Annotated

class ResumeInput(BaseModel):
    resume: Annotated[str,Field(...,description='Enter resume')]
    targetRole: Annotated[str,Field(...,description='Enter target Role')]
