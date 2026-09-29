import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchResumes, uploadResume } from "../api/resumes";
import { Card } from "../components/Card";
import { Badge } from "../components/Badge";
import { Skeleton } from "../components/Skeleton";
import { ErrorState } from "../components/ErrorState";
import { EmptyState } from "../components/EmptyState";
import { FileUploadInput } from "../components/FileUploadInput";
import { useToast } from "../hooks/useToast";
import type { Resume } from "../types";

function getSkills(resume: Resume): string[] {
  const skills = resume.extracted_data?.skills;

  if (!Array.isArray(skills)) {
    return [];
  }

  return skills.filter((skill): skill is string => typeof skill === "string");
}

function getExperience(resume: Resume): string {
  const experience = Number(resume.extracted_data?.experience_years ?? 0);
  return `${experience.toFixed(1)} yrs`;
}

function getEducation(resume: Resume): string {
  const education = resume.extracted_data?.education_level;
  return typeof education === "string" ? education : "none";
}

function statusVariant(status: string): "success" | "info" | "warning" | "danger" {
  if (status === "matched") {
    return "success";
  }

  if (status === "processed") {
    return "info";
  }

  if (status === "failed") {
    return "danger";
  }

  return "warning";
}

export function ResumesPage() {
  const queryClient = useQueryClient();
  const { push } = useToast();

  const resumesQuery = useQuery({
    queryKey: ["resumes"],
    queryFn: fetchResumes
  });

  const uploadMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["resumes"] });
      push("Resume uploaded and extracted", "success");
    },
    onError: error => {
      push(error instanceof Error ? error.message : "Upload failed", "error");
    }
  });

  const resumes = resumesQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Resumes</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Upload a single resume and inspect extracted skills, experience, and education.
        </p>
      </div>

      <Card title="Upload resume">
        <FileUploadInput
          label="Upload one PDF or DOCX resume"
          accept=".pdf,.docx"
          multiple={false}
          disabled={uploadMutation.isPending}
          onFiles={files => {
            if (files.length > 0) {
              uploadMutation.mutate(files[0]);
            }
          }}
        />
      </Card>

      {resumesQuery.isLoading && (
        <div className="space-y-3">
          <Skeleton className="h-12" />
          <Skeleton className="h-12" />
          <Skeleton className="h-12" />
        </div>
      )}

      {resumesQuery.isError && (
        <ErrorState
          message={resumesQuery.error instanceof Error ? resumesQuery.error.message : "Failed to load resumes"}
          onRetry={() => resumesQuery.refetch()}
        />
      )}

      {resumesQuery.isSuccess && resumes.length === 0 && (
        <EmptyState
          title="No resumes yet"
          description="Upload a resume to see skill extraction and profile parsing."
        />
      )}

      {resumesQuery.isSuccess && resumes.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3">Filename</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Skills</th>
                <th className="px-4 py-3">Experience</th>
                <th className="px-4 py-3">Education</th>
              </tr>
            </thead>
            <tbody>
              {resumes.map(resume => {
                const skills = getSkills(resume);

                return (
                  <tr
                    key={resume.id}
                    className="border-t border-slate-200 bg-white hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:hover:bg-slate-800/70"
                  >
                    <td className="px-4 py-3 font-medium">{resume.filename}</td>
                    <td className="px-4 py-3">
                      <Badge variant={statusVariant(resume.status)}>{resume.status}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {skills.slice(0, 5).map(skill => (
                          <Badge key={skill}>{skill}</Badge>
                        ))}
                        {skills.length === 0 && <Badge variant="neutral">No skills</Badge>}
                      </div>
                    </td>
                    <td className="px-4 py-3">{getExperience(resume)}</td>
                    <td className="px-4 py-3">{getEducation(resume)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
