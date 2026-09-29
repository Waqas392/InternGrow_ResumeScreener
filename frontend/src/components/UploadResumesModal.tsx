import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadResumes } from "../api/jobs";
import { Modal } from "./Modal";
import { Button } from "./Button";
import { FileUploadInput } from "./FileUploadInput";
import { useToast } from "../hooks/useToast";

interface UploadResumesModalProps {
  open: boolean;
  jobId: string;
  onClose: () => void;
}

export function UploadResumesModal({ open, jobId, onClose }: UploadResumesModalProps) {
  const queryClient = useQueryClient();
  const { push } = useToast();
  const [files, setFiles] = useState<File[]>([]);

  const uploadMutation = useMutation({
    mutationFn: () => uploadResumes(jobId, files),
    onSuccess: async response => {
      await queryClient.invalidateQueries({ queryKey: ["candidates", jobId] });
      await queryClient.invalidateQueries({ queryKey: ["resumes"] });
      push(`${response.accepted} resumes accepted for processing`, "success");
      setFiles([]);
      onClose();
    },
    onError: error => {
      push(error instanceof Error ? error.message : "Upload failed", "error");
    }
  });

  const tooManyFiles = files.length > 50;

  return (
    <Modal open={open} title="Upload resumes" onClose={onClose}>
      <div className="space-y-4">
        <FileUploadInput
          label="PDF or DOCX resumes, up to 50 files"
          accept=".pdf,.docx"
          multiple
          disabled={uploadMutation.isPending}
          onFiles={setFiles}
        />

        {tooManyFiles && (
          <p className="text-sm text-rose-600 dark:text-rose-400">
            Bulk upload is limited to 50 resumes.
          </p>
        )}

        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="button"
            loading={uploadMutation.isPending}
            disabled={files.length === 0 || tooManyFiles}
            onClick={() => uploadMutation.mutate()}
          >
            Upload and match
          </Button>
        </div>
      </div>
    </Modal>
  );
}
