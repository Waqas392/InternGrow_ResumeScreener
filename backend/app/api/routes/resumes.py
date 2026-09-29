from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.db.session import get_session
from app.db.models import User
from app.api.dependencies import get_current_user
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeResponse
from app.services.extraction_service import ExtractionService
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.core.config import settings

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await ResumeRepository(session).list_by_user(current_user.id)

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    resume = await ResumeRepository(session).get_by_id(resume_id)

    if resume is None:
        raise NotFoundException(detail="Resume not found")

    if resume.user_id != current_user.id:
        raise ForbiddenException()

    return resume

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    max_file_size = settings.max_file_size_mb * 1024 * 1024

    if len(content) > max_file_size:
        raise ValidationException(detail=f"File exceeds the {settings.max_file_size_mb}MB limit")

    filename = Path(file.filename or "resume").name
    lowered_name = filename.lower()

    if not lowered_name.endswith(".pdf") and not lowered_name.endswith(".docx"):
        raise ValidationException(detail="Only PDF and DOCX resumes are supported")

    extraction_service = ExtractionService()
    raw_text, profile = extraction_service.extract_resume(filename, content)

    repository = ResumeRepository(session)
    resume = await repository.create(
        user_id=current_user.id,
        filename=filename,
        raw_text=None,
        extracted_data=None
    )
    resume = await repository.update_extracted(resume, raw_text, profile)
    return resume
