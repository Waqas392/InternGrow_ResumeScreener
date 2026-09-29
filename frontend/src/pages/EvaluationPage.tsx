import { useQuery } from "@tanstack/react-query";
import { fetchEvaluation } from "../api/evaluation";
import type { EvaluationMetrics } from "../api/evaluation";
import { Card } from "../components/Card";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import { StatCard } from "../components/StatCard";

function MetricBar({ label, value }: { label: string; value: number }) {
  const percent = Math.round(value * 100);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-300">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-800">
        <div className="h-2 rounded-full bg-indigo-500" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function MetricsPanel({ title, metrics }: { title: string; metrics: EvaluationMetrics }) {
  return (
    <Card title={title}>
      <div className="space-y-4">
        <MetricBar label="Accuracy" value={metrics.accuracy} />
        <MetricBar label="Precision" value={metrics.precision} />
        <MetricBar label="Recall" value={metrics.recall} />
        <MetricBar label="F1" value={metrics.f1} />
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            <tr>
              <th className="px-3 py-2">True Positive</th>
              <th className="px-3 py-2">False Positive</th>
              <th className="px-3 py-2">True Negative</th>
              <th className="px-3 py-2">False Negative</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-t border-slate-200 dark:border-slate-800">
              <td className="px-3 py-2">{metrics.confusion_matrix.true_positive}</td>
              <td className="px-3 py-2">{metrics.confusion_matrix.false_positive}</td>
              <td className="px-3 py-2">{metrics.confusion_matrix.true_negative}</td>
              <td className="px-3 py-2">{metrics.confusion_matrix.false_negative}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function EvaluationPage() {
  const evaluationQuery = useQuery({
    queryKey: ["evaluation"],
    queryFn: fetchEvaluation
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Model evaluation</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Hybrid semantic and keyword screening compared against a keyword-only baseline.
        </p>
      </div>

      {evaluationQuery.isLoading && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-72" />
          <Skeleton className="h-72" />
        </div>
      )}

      {evaluationQuery.isError && (
        <ErrorState
          message={
            evaluationQuery.error instanceof Error
              ? evaluationQuery.error.message
              : "Failed to load evaluation"
          }
          onRetry={() => evaluationQuery.refetch()}
        />
      )}

      {evaluationQuery.data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Dataset size" value={evaluationQuery.data.dataset_size} />
            <StatCard label="Folds" value={evaluationQuery.data.folds} />
            <StatCard label="Decision threshold" value={evaluationQuery.data.threshold} />
            <StatCard label="Model F1" value={evaluationQuery.data.model.f1} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <MetricsPanel title="Hybrid model" metrics={evaluationQuery.data.model} />
            <MetricsPanel title="Keyword baseline" metrics={evaluationQuery.data.baseline} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <MetricsPanel
              title="Hybrid model cross-validation average"
              metrics={evaluationQuery.data.cross_validation.model}
            />
            <MetricsPanel
              title="Keyword baseline cross-validation average"
              metrics={evaluationQuery.data.cross_validation.baseline}
            />
          </div>
        </>
      )}
    </div>
  );
}
