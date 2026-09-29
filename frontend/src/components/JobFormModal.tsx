import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createJob } from "../api/jobs";
import { Modal } from "./Modal";
import { Input } from "./Input";
import { Button } from "./Button";
import { useToast } from "../hooks/useToast";

interface JobFormModalProps {
  open: boolean;
  onClose: () => void;
}

export function JobFormModal({ open, onClose }: JobFormModalProps) {
  const queryClient = useQueryClient();
  const { push } = useToast();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [formError, setFormError] = useState("");

  const createJobMutation = useMutation({
    mutationFn: createJob,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      push("Job created", "success");
      setTitle("");
      setDescription("");
      setRequiredSkills("");
      setFormError("");
      onClose();
    },
    onError: error => {
      push(error instanceof Error ? error.message : "Failed to create job", "error");
    }
  });

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError("");

    const skills = requiredSkills
      .split(",")
      .map(skill => skill.trim().toLowerCase())
      .filter(Boolean);

    if (title.trim().length < 3) {
      setFormError("Title must be at least 3 characters long");
      return;
    }

    if (description.trim().length < 10) {
      setFormError("Description must be at least 10 characters long");
      return;
    }

    if (skills.length === 0) {
      setFormError("Add at least one required skill");
      return;
    }

    createJobMutation.mutate({
      title: title.trim(),
      description: description.trim(),
      required_skills: skills
    });
  };

  return (
    <Modal open={open} title="Create job" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Job title"
          value={title}
          onChange={event => setTitle(event.target.value)}
          placeholder="Senior Python Engineer"
          required
        />
        <div className="space-y-1.5">
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
            Job description
          </label>
          <textarea
            value={description}
            onChange={event => setDescription(event.target.value)}
            placeholder="Write the job description, responsibilities, and requirements."
            rows={6}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition focus:ring-2 focus:ring-indigo-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          />
        </div>
        <Input
          label="Required skills"
          value={requiredSkills}
          onChange={event => setRequiredSkills(event.target.value)}
          placeholder="python, fastapi, sql, docker"
          required
        />
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Separate skills with commas.
        </p>

        {formError && <p className="text-sm text-rose-600 dark:text-rose-400">{formError}</p>}

        <div className="flex justify-end gap-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={createJobMutation.isPending}>
            Create job
          </Button>
        </div>
      </form>
    </Modal>
  );
}
