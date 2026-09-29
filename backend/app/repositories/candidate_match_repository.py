from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.db.models import CandidateMatch, Resume

class CandidateMatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        job_id: str,
        resume_id: str,
        overall_score: float,
        skill_score: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
        breakdown: dict
    ) -> CandidateMatch:
        result = await self.session.execute(
            select(CandidateMatch)
            .where(CandidateMatch.job_id == job_id)
            .where(CandidateMatch.resume_id == resume_id)
        )
        candidate = result.scalar_one_or_none()

        if candidate is None:
            candidate = CandidateMatch(
                job_id=job_id,
                resume_id=resume_id,
                overall_score=overall_score,
                skill_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                keyword_score=keyword_score,
                breakdown=breakdown
            )
            self.session.add(candidate)
        else:
            candidate.overall_score = overall_score
            candidate.skill_score = skill_score
            candidate.experience_score = experience_score
            candidate.education_score = education_score
            candidate.keyword_score = keyword_score
            candidate.breakdown = breakdown

        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate

    async def list_by_job(
        self,
        job_id: str,
        min_score: float | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[CandidateMatch], int]:
        query = (
            select(CandidateMatch)
            .options(selectinload(CandidateMatch.resume))
            .join(Resume, CandidateMatch.resume_id == Resume.id)
            .where(CandidateMatch.job_id == job_id)
        )

        if min_score is not None:
            query = query.where(CandidateMatch.overall_score >= min_score)

        if search:
            query = query.where(Resume.filename.ilike(f"%{search}%"))

        count_query = (
            select(func.count(CandidateMatch.id))
            .join(Resume, CandidateMatch.resume_id == Resume.id)
            .where(CandidateMatch.job_id == job_id)
        )

        if min_score is not None:
            count_query = count_query.where(CandidateMatch.overall_score >= min_score)

        if search:
            count_query = count_query.where(Resume.filename.ilike(f"%{search}%"))

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        result = await self.session.execute(
            query
            .order_by(desc(CandidateMatch.overall_score))
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().unique().all()), total
