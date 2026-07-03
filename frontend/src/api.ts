const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api/v1";

const TOKEN_KEY = "eris_demo_token";
const USER_KEY = "eris_demo_user";

export type AuthUser = {
  username: string;
  role: string;
  display_name: string;
  organization: string;
};

export type RegulatoryApplication = {
  id: string;
  reference_number: string;
  product_name: string;
  application_type: string;
  applicant_organization: string;
  dossier_summary: string;
  supporting_documents: string[];
  status: string;
  submitted_by: string;
  assigned_reviewer: string | null;
  last_comment: string | null;
  created_at: string;
  updated_at: string;
};

export type RegulatorySummary = {
  submitted: number;
  technical_review: number;
  clarification_requested: number;
  resubmitted: number;
  approved: number;
  rejected: number;
  total: number;
};

export type AuditTrailEvent = {
  id: string;
  action: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const authApi = {
  login: async (username: string, password: string) => {
    const result = await request<{
      access_token: string;
      username: string;
      role: string;
      display_name: string;
      organization: string;
    }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    localStorage.setItem(TOKEN_KEY, result.access_token);
    localStorage.setItem(
      USER_KEY,
      JSON.stringify({
        username: result.username,
        role: result.role,
        display_name: result.display_name,
        organization: result.organization,
      }),
    );
    return result;
  },
  me: () => request<AuthUser>("/auth/me"),
  logout: () => {
    clearAuth();
  },
};

export const regulatoryApi = {
  listApplications: (status?: string) =>
    request<RegulatoryApplication[]>(
      status ? `/regulatory/applications?status=${status}` : "/regulatory/applications",
    ),
  getApplication: (id: string) => request<RegulatoryApplication>(`/regulatory/applications/${id}`),
  submitApplication: (body: {
    product_name: string;
    application_type: string;
    applicant_organization: string;
    dossier_summary: string;
    supporting_documents?: string[];
  }) =>
    request<RegulatoryApplication>("/regulatory/applications", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  transition: (id: string, action: string, comment?: string) =>
    request<RegulatoryApplication>(`/regulatory/applications/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ action, comment }),
    }),
  resubmit: (
    id: string,
    body: { dossier_summary: string; supporting_documents?: string[]; applicant_note?: string },
  ) =>
    request<RegulatoryApplication>(`/regulatory/applications/${id}/resubmit`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  summary: () => request<RegulatorySummary>("/regulatory/dashboard/summary"),
  auditTrail: (id: string) =>
    request<AuditTrailEvent[]>(`/regulatory/applications/${id}/audit`),
};

// Re-export existing Q&A API from api.ts patterns
export type Citation = {
  chunk_id: string;
  title: string;
  source: string;
  excerpt: string;
  score: number;
};

export type Answer = {
  id: string;
  question_id: string;
  answer_text: string;
  citations: Citation[];
  risk_flags: string[];
  hallucination_flags: string[];
  refused: boolean;
  refusal_reason: string | null;
  review_status: string;
  reviewer_comment: string | null;
  disclaimer: string;
  created_at: string;
};

export type Question = {
  id: string;
  question_text: string;
  language: string;
  worker_id: string;
  approved_content_only: boolean;
  created_at: string;
};

export type QuestionDetail = {
  question: Question;
  latest_answer: Answer | null;
};

export type QASummary = {
  pending_review: number;
  approved: number;
  rejected: number;
  changes_requested: number;
  total_questions: number;
  total_answers: number;
  refused_answers: number;
};

export type AuditEvent = {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  synthetic_only: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type EvaluationResult = {
  total_questions: number;
  answered: number;
  refused: number;
  with_citations: number;
  passed: number;
  citation_rate: number;
  refusal_rate: number;
  pass_rate: number;
  avg_retrieval_score: number;
  results: Array<{
    question: string;
    language: string;
    expected_topic: string;
    answered: boolean;
    refused: boolean;
    has_citations: boolean;
    top_score: number;
    matched_topic: string | null;
    passed: boolean;
  }>;
  disclaimer: string;
};

export const api = {
  createQuestion: (body: {
    question_text: string;
    language: string;
    worker_id?: string;
    approved_content_only?: boolean;
  }) => request<Question>("/questions", { method: "POST", body: JSON.stringify(body) }),

  answerQuestion: (questionId: string) =>
    request<Answer>(`/questions/${questionId}/answer`, { method: "POST" }),

  getQuestion: (questionId: string) => request<QuestionDetail>(`/questions/${questionId}`),

  listQuestions: () => request<QuestionDetail[]>("/questions"),

  reviewAnswer: (answerId: string, action: string, reviewer_comment?: string) =>
    request<Answer>(`/answers/${answerId}/review`, {
      method: "POST",
      body: JSON.stringify({ action, reviewer_comment }),
    }),

  qaSummary: () => request<QASummary>("/dashboard/qa-summary"),

  runEvaluation: () => request<EvaluationResult>("/evaluation/run", { method: "POST" }),

  listAudit: (limit = 50) => request<AuditEvent[]>(`/audit?limit=${limit}`),
};
