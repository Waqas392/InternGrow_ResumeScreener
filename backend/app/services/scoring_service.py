from app.ai.nlp_extractor import NLPExtractor
from app.ai.semantic_matcher import resume_job_similarity

class ScoringService:
    def __init__(self):
        self.extractor = NLPExtractor()
        self.education_rank = {
            "none": 0,
            "associate": 1,
            "bachelor": 2,
            "master": 3,
            "phd": 4
        }
        self.education_weight = {
            "none": 0.2,
            "associate": 0.45,
            "bachelor": 0.7,
            "master": 0.85,
            "phd": 1.0
        }

    def score_candidate(
        self,
        raw_text: str,
        resume_profile: dict,
        job_description: str,
        required_skills: list[str]
    ) -> dict:
        required_skills_normalized = {skill.lower().strip() for skill in required_skills if skill.strip()}
        resume_skills_normalized = {skill.lower().strip() for skill in resume_profile.get("skills", []) if skill.strip()}

        matched_skills = sorted(required_skills_normalized.intersection(resume_skills_normalized))
        missing_skills = sorted(required_skills_normalized.difference(resume_skills_normalized))

        keyword_score = 1.0 if not required_skills_normalized else len(matched_skills) / len(required_skills_normalized)

        skill_score = resume_job_similarity(
            raw_text,
            job_description,
            sorted(resume_skills_normalized),
            sorted(required_skills_normalized)
        )

        job_profile = self.extractor.extract_profile(job_description)
        required_experience_years = job_profile.get("experience_years", 0.0)

        if required_experience_years <= 0:
            required_experience_years = 3.0

        candidate_experience_years = float(resume_profile.get("experience_years", 0.0))
        experience_score = min(candidate_experience_years / required_experience_years, 1.0)

        candidate_education = resume_profile.get("education_level", "none")
        required_education = job_profile.get("education_level", "none")

        if required_education == "none":
            education_score = self.education_weight.get(candidate_education, 0.5)
        else:
            candidate_rank = self.education_rank.get(candidate_education, 0)
            required_rank = self.education_rank.get(required_education, 0)

            if candidate_rank == 0:
                education_score = 0.2
            elif candidate_rank >= required_rank:
                education_score = 1.0
            else:
                education_score = candidate_rank / required_rank if required_rank else 1.0

        overall_score = (
            (0.45 * skill_score) +
            (0.25 * experience_score) +
            (0.15 * education_score) +
            (0.15 * keyword_score)
        )

        reasoning = (
            f"Matched {len(matched_skills)} of {len(required_skills_normalized)} required skills. "
            f"Candidate has {candidate_experience_years:.1f} years against an estimated requirement of {required_experience_years:.1f} years. "
            f"Education level detected as {candidate_education}. "
            f"Semantic similarity between resume and job description contributed {skill_score:.2f} to the skill score."
        )

        return {
            "skill_score": round(skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "keyword_score": round(keyword_score, 2),
            "overall_score": round(overall_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "reasoning": reasoning
        }
