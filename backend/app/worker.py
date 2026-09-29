from app.db.session import async_session
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.extraction_service import ExtractionService
from app.services.matching_service import MatchingService

async def process_uploaded_resumes(user_id: str, job_id: str, uploaded_files: list[dict]) -> None:
    async with async_session() as session:
        job_repository = JobRepository(session)
        resume_repository = ResumeRepository(session)
        extraction_service = ExtractionService()
        matching_service = MatchingService(session)

        job = await job_repository.get_by_id(job_id)

        if job is None or job.user_id != user_id:
            return

        for uploaded_file in uploaded_files:
            filename = uploaded_file["filename"]
            content = uploaded_file["content"]

            resume = await resume_repository.create(
                user_id=user_id,
                filename=filename,
                raw_text=None,
                extracted_data=None
            )

            try:
                raw_text, profile = extraction_service.extract_resume(filename, content)
                await resume_repository.update_extracted(resume, raw_text, profile)
                await matching_service.evaluate_resume_for_job(job, resume)
            except Exception:
                await resume_repository.update_status(resume, "failed")
