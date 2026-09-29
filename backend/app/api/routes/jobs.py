from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.db.session import get_session
from app.db.models import User, Job
from app.api.dependencies import get_current_user
from app.repositories.job_repository import JobRepository
from app.repositories.candidate_match_repository import CandidateMatchRepository
from app.schemas.job import JobCreate, JobResponse
from app.schemas.candidate import CandidatePage
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.core.config import settings
from app.worker import process_uploaded_resumes
from app.services.export_service import build_candidate_csv, build_candidate_pdf

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def serialize_candidates(matches: list, offset: int) -> list[dict]:
    items = []

    for index, match in enumerate(matches, start=offset + 1):
        breakdown = match.breakdown or {}

        items.append({
            "rank": index,
            "resume_id": match.resume_id,
            "filename": match.resume.filename if match.resume else "",
            "overall_score": match.overall_score,
            "skill_score": match.skill_score,
            "experience_score": match.experience_score,
            "education_score": match.education_score,
            "keyword_score": match.keyword_score,
            "matched_skills": breakdown.get("matched_skills", []),
            "missing_skills": breakdown.get("missing_skills", []),
            "reasoning": breakdown.get("reasoning", "")
        })

    return items

async def get_owned_job(job_id: str, current_user: User, session: AsyncSession) -> Job:
    job = await JobRepository(session).get_by_id(job_id)

    if job is None:
        raise NotFoundException(detail="Job not found")

    if job.user_id != current_user.id:
        raise ForbiddenException()

    return job

@router.post("", response_model=JobResponse)
async def create_job(
    payload: JobCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    normalized_skills = sorted({skill.lower().strip() for skill in payload.required_skills if skill.strip()})
    job = await JobRepository(session).create(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        required_skills=normalized_skills
    )
    return job

@router.get("", response_model=list[JobResponse])
async def list_jobs(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return await JobRepository(session).list_by_user(current_user.id)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = await get_owned_job(job_id, current_user, session)
    return job

@router.post("/{job_id}/resumes")
async def upload_resumes(
    job_id: str,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = await get_owned_job(job_id, current_user, session)

    if not files:
        raise ValidationException(detail="At least one resume file is required")

    if len(files) > settings.max_bulk_upload:
        raise ValidationException(detail=f"Bulk upload is limited to {settings.max_bulk_upload} files")

    max_file_size = settings.max_file_size_mb * 1024 * 1024
    uploaded_files = []

    for upload_file in files:
        content = await upload_file.read()

        if len(content) > max_file_size:
            raise ValidationException(detail=f"{upload_file.filename} exceeds the {settings.max_file_size_mb}MB limit")

        filename = Path(upload_file.filename or "resume").name
        lowered_name = filename.lower()

        if not lowered_name.endswith(".pdf") and not lowered_name.endswith(".docx"):
            raise ValidationException(detail="Only PDF and DOCX resumes are supported")

        uploaded_files.append({
            "filename": filename,
            "content": content
        })

    background_tasks.add_task(process_uploaded_resumes, current_user.id, job.id, uploaded_files)
    return {"accepted": len(uploaded_files)}

@router.get("/{job_id}/candidates", response_model=CandidatePage)
async def list_candidates(
    job_id: str,
    min_score: float | None = Query(default=None, ge=0, le=1),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    await get_owned_job(job_id, current_user, session)
    repository = CandidateMatchRepository(session)
    matches, total = await repository.list_by_job(
        job_id=job_id,
        min_score=min_score,
        search=search,
        limit=limit,
        offset=offset
    )
    items = serialize_candidates(matches, offset)
    return CandidatePage(items=items, total=total, limit=limit, offset=offset)

@router.get("/{job_id}/candidates/export/csv")
async def export_candidates_csv(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    await get_owned_job(job_id, current_user, session)
    repository = CandidateMatchRepository(session)
    matches, _ = await repository.list_by_job(job_id=job_id, limit=10000, offset=0)
    candidates = serialize_candidates(matches, 0)
    content = build_candidate_csv(candidates)

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=candidates_{job_id}.csv"}
    )

@router.get("/{job_id}/candidates/export/pdf")
async def export_candidates_pdf(
    job_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    await get_owned_job(job_id, current_user, session)
    repository = CandidateMatchRepository(session)
    matches, _ = await repository.list_by_job(job_id=job_id, limit=10000, offset=0)
    candidates = serialize_candidates(matches, 0)
    content = build_candidate_pdf(candidates)

    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=candidates_{job_id}.pdf"}
    )
