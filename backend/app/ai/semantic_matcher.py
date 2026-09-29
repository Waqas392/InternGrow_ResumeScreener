import hashlib
import threading
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.exceptions import ProcessingException

_model = None
_model_lock = threading.Lock()
_embedding_cache = {}

def get_model() -> SentenceTransformer:
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                try:
                    _model = SentenceTransformer(settings.sentence_transformer_model)
                except Exception as error:
                    raise ProcessingException(detail=f"Embedding model failed to load: {str(error)}")

    return _model

def encode_text(text: str) -> np.ndarray:
    normalized_text = " ".join(text.strip().split())

    if not normalized_text:
        return np.zeros(384)

    cache_key = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]

    model = get_model()
    embedding = model.encode(normalized_text, convert_to_numpy=True, normalize_embeddings=True)
    _embedding_cache[cache_key] = embedding
    return embedding

def cosine_similarity(first: np.ndarray, second: np.ndarray) -> float:
    first_norm = np.linalg.norm(first)
    second_norm = np.linalg.norm(second)

    if first_norm == 0 or second_norm == 0:
        return 0.0

    return float(np.dot(first, second) / (first_norm * second_norm))

def text_similarity(first_text: str, second_text: str) -> float:
    if not first_text or not second_text:
        return 0.0

    first_embedding = encode_text(first_text[:5000])
    second_embedding = encode_text(second_text[:5000])
    similarity = cosine_similarity(first_embedding, second_embedding)
    return max(0.0, min(1.0, similarity))

def resume_job_similarity(
    resume_text: str,
    job_description: str,
    resume_skills: list[str],
    required_skills: list[str]
) -> float:
    description_similarity = text_similarity(resume_text, job_description)

    resume_skill_text = ", ".join(resume_skills)
    required_skill_text = ", ".join(required_skills)
    skill_similarity = text_similarity(resume_skill_text, required_skill_text)

    combined = (0.7 * description_similarity) + (0.3 * skill_similarity)
    return max(0.0, min(1.0, combined))
