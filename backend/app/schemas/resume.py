from pydantic import BaseModel
from typing import Optional

class ResumeResponse(BaseModel):
    id: str
    filename: str
    status: str
    extracted_data: Optional[dict] = None

class ScoreBreakdown(BaseModel):
    skill_score: float
    experience_score: float
    education_score: float
    keyword_score: float
    overall_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasoning: str
