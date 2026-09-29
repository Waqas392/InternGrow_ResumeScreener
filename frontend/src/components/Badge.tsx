import type { ReactNode } from "react";

type BadgeVariant = "neutral" | "success" | "warning" | "danger" | "info";

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
}

const badgeClasses: Record<BadgeVariant, string> = {
  neutral: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100",
  success: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-100",
  warning: "bg-amber-100 text-amber-900 dark:bg-amber-900 dark:text-amber-100",
  danger: "bg-rose-100 text-rose-900 dark:bg-rose-900 dark:text-rose-100",
  info: "bg-sky-100 text-sky-900 dark:bg-sky-900 dark:text-sky-100"
};

export function Badge({ variant = "neutral", children }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${badgeClasses[variant]}`}>
      {children}
    </span>
  );
}
