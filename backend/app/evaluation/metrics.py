def confusion_matrix(y_true: list[int], y_pred: list[int]) -> dict:
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for actual, predicted in zip(y_true, y_pred):
        if actual == 1 and predicted == 1:
            true_positive += 1
        elif actual == 0 and predicted == 1:
            false_positive += 1
        elif actual == 0 and predicted == 0:
            true_negative += 1
        else:
            false_negative += 1

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative
    }

def precision_recall_f1_accuracy(y_true: list[int], y_pred: list[int]) -> dict:
    matrix = confusion_matrix(y_true, y_pred)

    true_positive = matrix["true_positive"]
    false_positive = matrix["false_positive"]
    true_negative = matrix["true_negative"]
    false_negative = matrix["false_negative"]

    total = true_positive + false_positive + true_negative + false_negative
    accuracy = (true_positive + true_negative) / total if total else 0.0

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if precision + recall else
        0.0
    )

    return {
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "confusion_matrix": matrix
    }

def average_metrics(metrics_list: list[dict]) -> dict:
    if not metrics_list:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "confusion_matrix": {
                "true_positive": 0,
                "false_positive": 0,
                "true_negative": 0,
                "false_negative": 0
            }
        }

    count = len(metrics_list)

    averaged_confusion = {
        "true_positive": round(sum(metric["confusion_matrix"]["true_positive"] for metric in metrics_list) / count),
        "false_positive": round(sum(metric["confusion_matrix"]["false_positive"] for metric in metrics_list) / count),
        "true_negative": round(sum(metric["confusion_matrix"]["true_negative"] for metric in metrics_list) / count),
        "false_negative": round(sum(metric["confusion_matrix"]["false_negative"] for metric in metrics_list) / count)
    }

    return {
        "accuracy": round(sum(metric["accuracy"] for metric in metrics_list) / count, 3),
        "precision": round(sum(metric["precision"] for metric in metrics_list) / count, 3),
        "recall": round(sum(metric["recall"] for metric in metrics_list) / count, 3),
        "f1": round(sum(metric["f1"] for metric in metrics_list) / count, 3),
        "confusion_matrix": averaged_confusion
    }
