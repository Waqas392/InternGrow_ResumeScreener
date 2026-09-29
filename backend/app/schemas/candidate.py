from pydantic import BaseModel

class CandidateResponse(BaseModel):
    rank: int
    resume_id: str
    filename: str
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    keyword_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    reasoning: str

class CandidatePage(BaseModel):
    items: list[CandidateResponse]
    total: int
    limit: int
    offset: int
