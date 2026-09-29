import { request } from "./client";

export interface ConfusionMatrix {
  true_positive: number;
  false_positive: number;
  true_negative: number;
  false_negative: number;
}

export interface EvaluationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  confusion_matrix: ConfusionMatrix;
}

export interface EvaluationReport {
  dataset_size: number;
  folds: number;
  threshold: number;
  model: EvaluationMetrics;
  baseline: EvaluationMetrics;
  cross_validation: {
    model: EvaluationMetrics;
    baseline: EvaluationMetrics;
  };
}

export async function fetchEvaluation(): Promise<EvaluationReport> {
  return request<EvaluationReport>("/api/evaluation/resume-screening");
}
