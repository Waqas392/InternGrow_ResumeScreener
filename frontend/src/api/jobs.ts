import { request, requestBlob } from "./client";
import type { CandidateFilters, CandidatePage, Job } from "../types";

export async function createJob(payload: {
  title: string;
  description: string;
  required_skills: string[];
}): Promise<Job> {
  return request<Job>("/api/jobs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function fetchJobs(): Promise<Job[]> {
  return request<Job[]>("/api/jobs");
}

export async function fetchJob(jobId: string): Promise<Job> {
  return request<Job>(`/api/jobs/${jobId}`);
}

export async function uploadResumes(jobId: string, files: File[]): Promise<{ accepted: number }> {
  const form = new FormData();

  for (const file of files) {
    form.append("files", file);
  }

  return request<{ accepted: number }>(`/api/jobs/${jobId}/resumes`, {
    method: "POST",
    body: form
  });
}

export async function fetchCandidates(jobId: string, filters: CandidateFilters): Promise<CandidatePage> {
  const query = new URLSearchParams();

  if (filters.min_score !== undefined) {
    query.set("min_score", String(filters.min_score));
  }

  if (filters.search) {
    query.set("search", filters.search);
  }

  if (filters.limit !== undefined) {
    query.set("limit", String(filters.limit));
  }

  if (filters.offset !== undefined) {
    query.set("offset", String(filters.offset));
  }

  return request<CandidatePage>(`/api/jobs/${jobId}/candidates?${query.toString()}`);
}

export async function exportCandidatesCsv(jobId: string): Promise<Blob> {
  return requestBlob(`/api/jobs/${jobId}/candidates/export/csv`);
}

export async function exportCandidatesPdf(jobId: string): Promise<Blob> {
  return requestBlob(`/api/jobs/${jobId}/candidates/export/pdf`);
}
