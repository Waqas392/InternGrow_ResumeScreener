import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "../api/jobs";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Badge } from "../components/Badge";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import { StatCard } from "../components/StatCard";
import { JobFormModal } from "../components/JobFormModal";

export function DashboardPage() {
  const [showJobModal, setShowJobModal] = useState(false);

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: fetchJobs
  });

  const jobs = jobsQuery.data ?? [];
  const uniqueSkills = new Set(jobs.flatMap(job => job.required_skills)).size;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Create jobs, upload resumes, and rank candidates.
          </p>
        </div>
        <Button onClick={() => setShowJobModal(true)}>Create job</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Total jobs" value={jobs.length} />
        <StatCard label="Unique required skills" value={uniqueSkills} />
        <StatCard label="Bulk upload limit" value="50 resumes" />
      </div>

      {jobsQuery.isLoading && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-36" />
          <Skeleton className="h-36" />
          <Skeleton className="h-36" />
          <Skeleton className="h-36" />
        </div>
      )}

      {jobsQuery.isError && (
        <ErrorState
          message={jobsQuery.error instanceof Error ? jobsQuery.error.message : "Failed to load jobs"}
          onRetry={() => jobsQuery.refetch()}
        />
      )}

      {jobsQuery.isSuccess && jobs.length === 0 && (
        <EmptyState
          title="No jobs yet"
          description="Create your first job to start uploading resumes and ranking candidates."
          action={<Button onClick={() => setShowJobModal(true)}>Create job</Button>}
        />
      )}

      {jobsQuery.isSuccess && jobs.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          {jobs.map(job => (
            <Card key={job.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <Link
                    to={`/jobs/${job.id}`}
                    className="text-lg font-semibold hover:text-indigo-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:text-indigo-400"
                  >
                    {job.title}
                  </Link>
                  <p className="mt-2 line-clamp-3 text-sm text-slate-600 dark:text-slate-300">
                    {job.description}
                  </p>
                </div>
                <Badge variant="info">{job.required_skills.length} skills</Badge>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {job.required_skills.slice(0, 6).map(skill => (
                  <Badge key={skill}>{skill}</Badge>
                ))}
              </div>

              <div className="mt-5">
                <Link
                  to={`/jobs/${job.id}`}
                  className="inline-flex rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  View candidates
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}

      <JobFormModal open={showJobModal} onClose={() => setShowJobModal(false)} />
    </div>
  );
}
