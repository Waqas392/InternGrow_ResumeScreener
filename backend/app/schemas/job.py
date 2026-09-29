from pydantic import BaseModel, Field

class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    required_skills: list[str]

class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    required_skills: list[str]
