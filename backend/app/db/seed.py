from app.core.config import settings
from app.core.security import hash_password
from app.db.session import async_session
from app.repositories.user_repository import UserRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.ai.nlp_extractor import NLPExtractor
from app.services.matching_service import MatchingService

async def seed_demo_data() -> None:
    if not settings.seed_email or not settings.seed_password:
        return

    async with async_session() as session:
        user_repository = UserRepository(session)
        existing_user = await user_repository.get_by_email(settings.seed_email)

        if existing_user is not None:
            return

        user = await user_repository.create(
            email=settings.seed_email,
            hashed_password=hash_password(settings.seed_password)
        )

        job_repository = JobRepository(session)
        job = await job_repository.create(
            user_id=user.id,
            title="Senior Python Engineer",
            description=(
                "We are looking for a senior Python engineer with production experience in FastAPI, "
                "SQLAlchemy, REST APIs, Docker, and automated testing. You will build AI-powered "
                "services, design clean APIs, and ship reliable backend systems."
            ),
            required_skills=["python", "fastapi", "sql", "docker", "pytest", "restapi"]
        )

        resume_text = (
            "Ayesha Khan\n"
            "Karachi, Pakistan\n"
            "ayesha.khan@example.com\n"
            "+92 300 1234567\n\n"
            "Senior Python Engineer with 6 years of experience building backend systems.\n"
            "Experienced with Python, FastAPI, SQL, Docker, pytest, REST API design, and CI/CD.\n"
            "Built resume screening pipelines, document processing systems, and analytics dashboards.\n"
            "Bachelor of Science in Computer Science.\n"
        )

        extractor = NLPExtractor()
        profile = extractor.extract_profile(resume_text)

        resume_repository = ResumeRepository(session)
        resume = await resume_repository.create(
            user_id=user.id,
            filename="demo_resume.pdf",
            raw_text=None,
            extracted_data=None
        )
        resume = await resume_repository.update_extracted(resume, resume_text, profile)

        matching_service = MatchingService(session)
        await matching_service.evaluate_resume_for_job(job, resume)
