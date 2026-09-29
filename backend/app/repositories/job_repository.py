from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import Job

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, title: str, description: str, required_skills: list[str]) -> Job:
        job = Job(
            user_id=user_id,
            title=title,
            description=description,
            required_skills=required_skills
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def list_by_user(self, user_id: str) -> list[Job]:
        result = await self.session.execute(
            select(Job)
            .where(Job.user_id == user_id)
            .order_by(Job.title.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, job_id: str) -> Job | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def get_with_candidates(self, job_id: str) -> Job | None:
        result = await self.session.execute(
            select(Job)
            .options(selectinload(Job.candidates))
            .where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
