import { Fragment, useState } from "react";
import type { Candidate } from "../types";
import { Badge } from "./Badge";
import { ScoreBar } from "./ScoreBar";

interface CandidateTableProps {
  candidates: Candidate[];
}

function scoreVariant(score: number): "success" | "warning" | "danger" {
  if (score >= 0.75) {
    return "success";
  }

  if (score >= 0.5) {
    return "warning";
  }

  return "danger";
}

export function CandidateTable({ candidates }: CandidateTableProps) {
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  const toggleRow = (resumeId: string) => {
    setExpandedRows(previous => ({
      ...previous,
      [resumeId]: !previous[resumeId]
    }));
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">
          <tr>
            <th className="px-4 py-3">Rank</th>
            <th className="px-4 py-3">Candidate</th>
            <th className="px-4 py-3">Overall</th>
            <th className="px-4 py-3">Skill</th>
            <th className="px-4 py-3">Experience</th>
            <th className="px-4 py-3">Education</th>
            <th className="px-4 py-3">Keyword</th>
            <th className="px-4 py-3">Details</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map(candidate => {
            const expanded = Boolean(expandedRows[candidate.resume_id]);

            return (
              <Fragment key={candidate.resume_id}>
                <tr className="border-t border-slate-200 bg-white hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:hover:bg-slate-800/70">
                  <td className="px-4 py-3 font-semibold">{candidate.rank}</td>
                  <td className="px-4 py-3">{candidate.filename}</td>
                  <td className="px-4 py-3">
                    <Badge variant={scoreVariant(candidate.overall_score)}>
                      {Math.round(candidate.overall_score * 100)}%
                    </Badge>
                  </td>
                  <td className="px-4 py-3">{Math.round(candidate.skill_score * 100)}%</td>
                  <td className="px-4 py-3">{Math.round(candidate.experience_score * 100)}%</td>
                  <td className="px-4 py-3">{Math.round(candidate.education_score * 100)}%</td>
                  <td className="px-4 py-3">{Math.round(candidate.keyword_score * 100)}%</td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => toggleRow(candidate.resume_id)}
                      aria-expanded={expanded}
                      className="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:border-slate-700 dark:hover:bg-slate-800"
                    >
                      {expanded ? "Hide" : "Explain"}
                    </button>
                  </td>
                </tr>

                {expanded && (
                  <tr className="border-t border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-950/60">
                    <td colSpan={8} className="px-4 py-4">
                      <div className="grid gap-4 lg:grid-cols-2">
                        <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
                          <ScoreBar label="Semantic skill fit" score={candidate.skill_score} />
                          <ScoreBar label="Experience fit" score={candidate.experience_score} />
                          <ScoreBar label="Education fit" score={candidate.education_score} />
                          <ScoreBar label="Keyword overlap" score={candidate.keyword_score} />
                          <ScoreBar label="Overall score" score={candidate.overall_score} />
                        </div>

                        <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
                          <div>
                            <h3 className="text-sm font-semibold">Matched skills</h3>
                            <div className="mt-2 flex flex-wrap gap-2">
                              {candidate.matched_skills.length > 0 ? (
                                candidate.matched_skills.map(skill => (
                                  <Badge key={skill} variant="success">
                                    {skill}
                                  </Badge>
                                ))
                              ) : (
                                <Badge variant="neutral">None</Badge>
                              )}
                            </div>
                          </div>

                          <div>
                            <h3 className="text-sm font-semibold">Missing skills</h3>
                            <div className="mt-2 flex flex-wrap gap-2">
                              {candidate.missing_skills.length > 0 ? (
                                candidate.missing_skills.map(skill => (
                                  <Badge key={skill} variant="danger">
                                    {skill}
                                  </Badge>
                                ))
                              ) : (
                                <Badge variant="neutral">None</Badge>
                              )}
                            </div>
                          </div>

                          <div>
                            <h3 className="text-sm font-semibold">Reasoning</h3>
                            <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-300">
                              {candidate.reasoning}
                            </p>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
