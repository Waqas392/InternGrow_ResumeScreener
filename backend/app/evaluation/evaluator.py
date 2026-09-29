import threading
from app.evaluation.dataset import EVALUATION_SAMPLES
from app.evaluation.metrics import precision_recall_f1_accuracy, average_metrics
from app.ai.nlp_extractor import NLPExtractor
from app.services.scoring_service import ScoringService

_cache = None
_cache_lock = threading.Lock()

def baseline_keyword_score(resume_skills: list[str], required_skills: list[str]) -> float:
    required_normalized = {skill.lower().strip() for skill in required_skills if skill.strip()}

    if not required_normalized:
        return 0.0

    resume_normalized = {skill.lower().strip() for skill in resume_skills if skill.strip()}
    matched = required_normalized.intersection(resume_normalized)
    return len(matched) / len(required_normalized)

def k_fold_metrics(scores: list[float], labels: list[int], threshold: float, folds: int) -> dict:
    fold_metrics = []
    indices = list(range(len(scores)))

    for fold_index in range(folds):
        test_indices = indices[fold_index::folds]

        if not test_indices:
            continue

        y_true = [labels[index] for index in test_indices]
        y_pred = [1 if scores[index] >= threshold else 0 for index in test_indices]
        fold_metrics.append(precision_recall_f1_accuracy(y_true, y_pred))

    return average_metrics(fold_metrics)

def build_report() -> dict:
    extractor = NLPExtractor()
    scoring_service = ScoringService()

    y_true = []
    model_scores = []
    baseline_scores = []

    for sample in EVALUATION_SAMPLES:
        resume_profile = extractor.extract_profile(sample["resume_text"])

        score = scoring_service.score_candidate(
            raw_text=sample["resume_text"],
            resume_profile=resume_profile,
            job_description=sample["job_description"],
            required_skills=sample["required_skills"]
        )

        y_true.append(int(sample["label"]))
        model_scores.append(float(score["overall_score"]))
        baseline_scores.append(
            baseline_keyword_score(
                resume_profile.get("skills", []),
                sample["required_skills"]
            )
        )

    threshold = 0.5

    model_predictions = [1 if score >= threshold else 0 for score in model_scores]
    baseline_predictions = [1 if score >= threshold else 0 for score in baseline_scores]

    model_metrics = precision_recall_f1_accuracy(y_true, model_predictions)
    baseline_metrics = precision_recall_f1_accuracy(y_true, baseline_predictions)

    folds = min(3, len(EVALUATION_SAMPLES))
    model_cv = k_fold_metrics(model_scores, y_true, threshold, folds)
    baseline_cv = k_fold_metrics(baseline_scores, y_true, threshold, folds)

    return {
        "dataset_size": len(EVALUATION_SAMPLES),
        "folds": folds,
        "threshold": threshold,
        "model": model_metrics,
        "baseline": baseline_metrics,
        "cross_validation": {
            "model": model_cv,
            "baseline": baseline_cv
        }
    }

def get_evaluation_report() -> dict:
    global _cache

    if _cache is not None:
        return _cache

    with _cache_lock:
        if _cache is None:
            _cache = build_report()

    return _cache
