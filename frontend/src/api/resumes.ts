import { request } from "./client";
import type { Resume } from "../types";

export async function fetchResumes(): Promise<Resume[]> {
  return request<Resume[]>("/api/resumes");
}

export async function uploadResume(file: File): Promise<Resume> {
  const form = new FormData();
  form.append("file", file);

  return request<Resume>("/api/resumes/upload", {
    method: "POST",
    body: form
  });
}
