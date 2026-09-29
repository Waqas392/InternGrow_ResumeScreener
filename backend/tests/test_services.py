from app.evaluation.metrics import precision_recall_f1_accuracy, confusion_matrix
from app.core.security import hash_password, verify_password

def test_confusion_matrix():
    y_true = [1, 0, 1, 0]
    y_pred = [1, 0, 0, 1]

    matrix = confusion_matrix(y_true, y_pred)

    assert matrix["true_positive"] == 1
    assert matrix["true_negative"] == 1
    assert matrix["false_positive"] == 1
    assert matrix["false_negative"] == 1

def test_classification_metrics():
    y_true = [1, 1, 0, 0]
    y_pred = [1, 1, 0, 0]

    metrics = precision_recall_f1_accuracy(y_true, y_pred)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0

def test_password_hashing():
    password = "StrongPass123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password("WrongPass123!", hashed)
