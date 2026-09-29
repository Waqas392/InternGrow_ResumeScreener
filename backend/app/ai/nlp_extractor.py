import re
import spacy
from spacy.matcher import PhraseMatcher
from app.core.config import settings
from app.ai.skills_taxonomy import SKILL_TAXONOMY
from app.ai.profile_parsers import years_from_date_ranges, education_level

class NLPExtractor:
    def __init__(self):
        self.nlp = self.load_model()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.build_matcher()

        self.email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.phone_regex = re.compile(
            r"(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?)?\d{3,4}[\s.-]?\d{4}"
        )
        self.experience_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:\+|\-)?\s*(?:years?|yrs?)\b",
            r"(\d+(?:\.\d+)?)\s*(?:\+|\-)?\s*years?'?\s*(?:of\s+)?(?:experience|exp)"
        ]

    def load_model(self):
        try:
            return spacy.load(settings.spacy_model, disable=["ner", "lemmatizer"])
        except OSError:
            return spacy.blank("en")

    def build_matcher(self):
        for canonical_skill, synonyms in SKILL_TAXONOMY.items():
            patterns = [self.nlp.make_doc(synonym.lower()) for synonym in synonyms]
            patterns.append(self.nlp.make_doc(canonical_skill.lower()))
            self.matcher.add(canonical_skill, patterns)

    def extract_skills(self, text: str) -> list[str]:
        if not text:
            return []

        doc = self.nlp(text)
        matches = self.matcher(doc)
        skills = set()

        for match_id, start, end in matches:
            canonical_skill = self.nlp.vocab.strings[match_id]
            skills.add(canonical_skill.lower())

        return sorted(skills)

    def extract_experience_years(self, text: str) -> float:
        if not text:
            return 0.0

        explicit = []
        for pattern in self.experience_patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                try:
                    explicit.append(float(match.group(1)))
                except ValueError:
                    continue

        explicit = [value for value in explicit if value <= 40]
        return max(years_from_date_ranges(text), max(explicit, default=0.0))

    def extract_education_level(self, text: str) -> str:
        if not text:
            return "none"
        return education_level(text)

    def extract_emails(self, text: str) -> list[str]:
        if not text:
            return []
        return sorted(set(self.email_regex.findall(text)))

    def extract_phones(self, text: str) -> list[str]:
        if not text:
            return []
        return sorted(set(self.phone_regex.findall(text)))

    def extract_profile(self, text: str) -> dict:
        return {
            "skills": self.extract_skills(text),
            "experience_years": self.extract_experience_years(text),
            "education_level": self.extract_education_level(text),
            "emails": self.extract_emails(text),
            "phones": self.extract_phones(text)
        }
