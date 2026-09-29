from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Resume

class ResumeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, filename: str, raw_text: str | None = None, extracted_data: dict | None = None) -> Resume:
        resume = Resume(
            user_id=user_id,
            filename=filename,
            raw_text=raw_text,
            extracted_data=extracted_data,
            status="pending"
        )
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: str) -> Resume | None:
        result = await self.session.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Resume]:
        result = await self.session.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.filename.asc())
        )
        return list(result.scalars().all())

    async def update_extracted(self, resume: Resume, raw_text: str, extracted_data: dict) -> Resume:
        resume.raw_text = raw_text
        resume.extracted_data = extracted_data
        resume.status = "processed"
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def update_status(self, resume: Resume, status: str) -> Resume:
        resume.status = status
        await self.session.commit()
        await self.session.refresh(resume)
        return resume
