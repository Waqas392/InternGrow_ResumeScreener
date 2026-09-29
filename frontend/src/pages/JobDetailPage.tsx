import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchCandidates, fetchJob, exportCandidatesCsv, exportCandidatesPdf } from "../api/jobs";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import { CandidateTable } from "../components/CandidateTable";
import { UploadResumesModal } from "../components/UploadResumesModal";
import { useToast } from "../hooks/useToast";
import { downloadBlob } from "../utils/download";
import type { CandidateFilters } from "../types";

const PAGE_SIZE = 20;

export function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const { push } = useToast();

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchInput, setSearchInput] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [offset, setOffset] = useState(0);
  const [exporting, setExporting] = useState<"csv" | "pdf" | null>(null);

  const filters: CandidateFilters = {
    search: appliedSearch || undefined,
    min_score: minScore,
    limit: PAGE_SIZE,
    offset
  };

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId ?? ""),
    enabled: Boolean(jobId)
  });

  const candidatesQuery = useQuery({
    queryKey: ["candidates", jobId, filters],
    queryFn: () => fetchCandidates(jobId ?? "", filters),
    enabled: Boolean(jobId)
  });

  if (!jobId) {
    return <ErrorState message="Job not found" />;
  }

  const handleExportCsv = async () => {
    setExporting("csv");

    try {
      const blob = await exportCandidatesCsv(jobId);
      downloadBlob(blob, `candidates_${jobId}.csv`);
      push("CSV exported", "success");
    } catch (error) {
      push(error instanceof Error ? error.message : "CSV export failed", "error");
    } finally {
      setExporting(null);
    }
  };

  const handleExportPdf = async () => {
    setExporting("pdf");

    try {
      const blob = await exportCandidatesPdf(jobId);
      downloadBlob(blob, `candidates_${jobId}.pdf`);
      push("PDF exported", "success");
    } catch (error) {
      push(error instanceof Error ? error.message : "PDF export failed", "error");
    } finally {
      setExporting(null);
    }
  };

  const candidates = candidatesQuery.data?.items ?? [];
  const totalCandidates = candidatesQuery.data?.total ?? 0;
  const hasPrevious = offset > 0;
  const hasNext = offset + PAGE_SIZE < totalCandidates;

  return (
    <div className="space-y-6">
      {jobQuery.isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-10 w-72" />
          <Skeleton className="h-24" />
          <Skeleton className="h-12 w-full max-w-xl" />
        </div>
      )}

      {jobQuery.isError && (
        <ErrorState
          message={jobQuery.error instanceof Error ? jobQuery.error.message : "Failed to load job"}
          onRetry={() => jobQuery.refetch()}
        />
      )}

      {jobQuery.data && (
        <>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-3xl space-y-3">
              <h1 className="text-2xl font-semibold tracking-tight">{jobQuery.data.title}</h1>
              <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">
                {jobQuery.data.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {jobQuery.data.required_skills.map(skill => (
                  <Badge key={skill}>{skill}</Badge>
                ))}
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" onClick={() => setShowUploadModal(true)}>
                Upload resumes
              </Button>
              <Button variant="secondary" onClick={handleExportCsv} loading={exporting === "csv"}>
                Export CSV
              </Button>
              <Button variant="secondary" onClick={handleExportPdf} loading={exporting === "pdf"}>
                Export PDF
              </Button>
            </div>
          </div>

          <Card title="Filters">
            <div className="grid gap-4 md:grid-cols-3">
              <form
                onSubmit={event => {
                  event.preventDefault();
                  setAppliedSearch(searchInput.trim());
                  setOffset(0);
                }}
                className="space-y-2"
              >
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Search resume filename
                </label>
                <div className="flex gap-2">
                  <input
                    value={searchInput}
                    onChange={event => setSearchInput(event.target.value)}
                    placeholder="candidate_resume.pdf"
                    className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900"
                  />
                  <Button type="submit" variant="secondary">
                    Apply
                  </Button>
                </div>
              </form>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Minimum overall score
                </label>
                <select
                  value={minScore === undefined ? "" : String(minScore)}
                  onChange={event => {
                    const value = event.target.value;
                    setMinScore(value === "" ? undefined : Number(value));
                    setOffset(0);
                  }}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900"
                >
                  <option value="">Any</option>
                  <option value="0.1">0.1</option>
                  <option value="0.2">0.2</option>
                  <option value="0.3">0.3</option>
                  <option value="0.4">0.4</option>
                  <option value="0.5">0.5</option>
                  <option value="0.6">0.6</option>
                  <option value="0.7">0.7</option>
                  <option value="0.8">0.8</option>
                  <option value="0.9">0.9</option>
                </select>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-slate-700 dark:text-slate-200">Result summary</p>
                <p className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 dark:border-slate-800 dark:text-slate-300">
                  {totalCandidates} candidates
                </p>
              </div>
            </div>
          </Card>

          {candidatesQuery.isLoading && (
            <div className="space-y-3">
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
              <Skeleton className="h-12" />
            </div>
          )}

          {candidatesQuery.isError && (
            <ErrorState
              message={
                candidatesQuery.error instanceof Error
                  ? candidatesQuery.error.message
                  : "Failed to load candidates"
              }
              onRetry={() => candidatesQuery.refetch()}
            />
          )}

          {candidatesQuery.isSuccess && candidates.length === 0 && (
            <EmptyState
              title="No candidates found"
              description="Upload resumes for this job or adjust the filters."
              action={<Button onClick={() => setShowUploadModal(true)}>Upload resumes</Button>}
            />
          )}

          {candidatesQuery.isSuccess && candidates.length > 0 && (
            <div className="space-y-4">
              <CandidateTable candidates={candidates} />

              <div className="flex flex-wrap items-center justify-between gap-4">
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  Showing {offset + 1} to {Math.min(offset + PAGE_SIZE, totalCandidates)} of {totalCandidates}
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="secondary"
                    disabled={!hasPrevious}
                    onClick={() => setOffset(previous => Math.max(previous - PAGE_SIZE, 0))}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={!hasNext}
                    onClick={() => setOffset(previous => previous + PAGE_SIZE)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </div>
          )}

          <UploadResumesModal
            open={showUploadModal}
            jobId={jobId}
            onClose={() => setShowUploadModal(false)}
          />
        </>
      )}
    </div>
  );
}
