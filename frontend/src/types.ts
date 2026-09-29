export interface User {
  id: string;
  email: string;
}

export interface Job {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
}

export interface Resume {
  id: string;
  filename: string;
  status: string;
  extracted_data: Record<string, unknown> | null;
}

export interface Candidate {
  rank: number;
  resume_id: string;
  filename: string;
  overall_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  keyword_score: number;
  matched_skills: string[];
  missing_skills: string[];
  reasoning: string;
}

export interface CandidatePage {
  items: Candidate[];
  total: number;
  limit: number;
  offset: number;
}

export interface CandidateFilters {
  min_score?: number;
  search?: string;
  limit?: number;
  offset?: number;
}
