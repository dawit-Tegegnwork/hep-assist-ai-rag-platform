const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api/v1";

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
  citation_rate: number;
  refusal_rate: number;
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
  }>;
  disclaimer: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

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
