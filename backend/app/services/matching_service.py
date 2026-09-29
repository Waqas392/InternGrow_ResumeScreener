from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Job, Resume
from app.core.exceptions import ProcessingException
from app.repositories.resume_repository import ResumeRepository
from app.repositories.candidate_match_repository import CandidateMatchRepository
from app.services.scoring_service import ScoringService
from app.ai.nlp_extractor import NLPExtractor

class MatchingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.resume_repository = ResumeRepository(session)
        self.candidate_repository = CandidateMatchRepository(session)
        self.scoring_service = ScoringService()
        self.extractor = NLPExtractor()

    async def evaluate_resume_for_job(self, job: Job, resume: Resume) -> None:
        try:
            if not resume.raw_text:
                raise ProcessingException(detail="Resume has no extracted text")

            resume_profile = resume.extracted_data

            if not resume_profile:
                resume_profile = self.extractor.extract_profile(resume.raw_text)
                await self.resume_repository.update_extracted(resume, resume.raw_text, resume_profile)

            score = self.scoring_service.score_candidate(
                raw_text=resume.raw_text,
                resume_profile=resume_profile,
                job_description=job.description,
                required_skills=job.required_skills
            )

            await self.candidate_repository.upsert(
                job_id=job.id,
                resume_id=resume.id,
                overall_score=score["overall_score"],
                skill_score=score["skill_score"],
                experience_score=score["experience_score"],
                education_score=score["education_score"],
                keyword_score=score["keyword_score"],
                breakdown=score
            )

            await self.resume_repository.update_status(resume, "matched")
        except Exception:
            await self.resume_repository.update_status(resume, "failed")
            raise

    async def process_job_resumes(self, job: Job, resume_ids: list[str]) -> None:
        for resume_id in resume_ids:
            resume = await self.resume_repository.get_by_id(resume_id)

            if resume is None:
                continue

            await self.evaluate_resume_for_job(job, resume)
