from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ClinicalPreprocessInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)


class ClinicalPreprocessOutput(BaseModel):
    original: str
    cleaned: str
    normalized: str
    redactions: list[str]
    token_count: int


class GuidelineSearchInput(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    limit: int = Field(default=3, ge=1, le=5)


class GuidelineChunk(BaseModel):
    id: str
    title: str
    source: str
    summary: str
    score: float
    language: str = "en"


class GuidelineSearchOutput(BaseModel):
    query: str
    matches: list[GuidelineChunk]
    disclaimer: str = "Synthetic guideline snippets for portfolio demo use only."


class SoapNoteInput(BaseModel):
    chief_complaint: str = Field(..., min_length=1, max_length=500)
    history: str = Field(..., min_length=1, max_length=3000)
    vitals: dict[str, str | float | int] = Field(default_factory=dict)
    problems: list[str] = Field(default_factory=list, max_length=10)


class SoapNoteOutput(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: list[str]
    safety_note: str
    disclaimer: str = "Draft generated from synthetic demo input; not medical advice."


class AuditEvent(BaseModel):
    action: str
    synthetic_only: bool = True
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NoteCreateInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    raw_text: str = Field(..., min_length=1, max_length=8000)
    note_type: str = Field(default="clinical", max_length=50)


class NoteResponse(BaseModel):
    id: UUID
    title: str
    raw_text: str
    note_type: str
    created_at: datetime


class ExtractionResponse(BaseModel):
    id: UUID
    note_id: UUID
    summary: str
    follow_up_tasks: list[str]
    risk_flags: list[str]
    structured_payload: dict[str, object]
    review_status: str
    reviewer_comment: str | None
    reviewed_at: datetime | None
    provider: str
    created_at: datetime


class NoteDetailResponse(BaseModel):
    note: NoteResponse
    latest_extraction: ExtractionResponse | None


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"


class ReviewInput(BaseModel):
    action: ReviewAction
    reviewer_comment: str | None = Field(default=None, max_length=1000)


class DashboardSummary(BaseModel):
    pending_review: int
    approved: int
    rejected: int
    changes_requested: int
    total_notes: int
    total_extractions: int


class DashboardReviewRow(BaseModel):
    note_title: str
    summary: str
    review_status: str
    note_type: str


class AuditEventResponse(BaseModel):
    id: UUID
    action: str
    entity_type: str
    entity_id: str | None
    synthetic_only: bool
    metadata: dict[str, object]
    created_at: datetime


class Citation(BaseModel):
    chunk_id: str
    title: str
    source: str
    excerpt: str
    score: float


class QuestionCreateInput(BaseModel):
    question_text: str = Field(..., min_length=3, max_length=2000)
    language: str = Field(default="en", max_length=10)
    worker_id: str = Field(default="synthetic-worker-001", max_length=50)
    approved_content_only: bool = True


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    language: str
    worker_id: str
    approved_content_only: bool
    created_at: datetime


class AnswerResponse(BaseModel):
    id: UUID
    question_id: UUID
    answer_text: str
    citations: list[Citation]
    risk_flags: list[str]
    hallucination_flags: list[str]
    refused: bool
    refusal_reason: str | None
    review_status: str
    reviewer_comment: str | None
    reviewed_at: datetime | None
    retrieval_scores: list[float]
    approved_content_only: bool
    provider: str
    disclaimer: str = "Synthetic demo answer; not medical advice. Human review required."
    created_at: datetime


class QuestionDetailResponse(BaseModel):
    question: QuestionResponse
    latest_answer: AnswerResponse | None


class QADashboardSummary(BaseModel):
    pending_review: int
    approved: int
    rejected: int
    changes_requested: int
    total_questions: int
    total_answers: int
    refused_answers: int


class EvaluationCaseResult(BaseModel):
    question: str
    language: str
    expected_topic: str
    answered: bool
    refused: bool
    has_citations: bool
    top_score: float
    matched_topic: str | None
    passed: bool


class EvaluationResult(BaseModel):
    total_questions: int
    answered: int
    refused: int
    with_citations: int
    passed: int
    citation_rate: float
    refusal_rate: float
    pass_rate: float
    avg_retrieval_score: float
    results: list[EvaluationCaseResult]
    disclaimer: str = "Evaluation uses synthetic golden questions only; not clinical validation."

