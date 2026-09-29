import asyncio
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.db.models import User
from app.evaluation.evaluator import get_evaluation_report

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

@router.get("/resume-screening")
async def resume_screening_evaluation(_: User = Depends(get_current_user)):
    return await asyncio.to_thread(get_evaluation_report)
