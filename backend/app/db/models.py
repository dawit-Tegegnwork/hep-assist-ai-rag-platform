from datetime import UTC, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class ClinicalNote(SQLModel, table=True):
    __tablename__ = "clinical_notes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200)
    raw_text: str
    note_type: str = Field(default="clinical", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Extraction(SQLModel, table=True):
    __tablename__ = "extractions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    note_id: UUID = Field(foreign_key="clinical_notes.id", index=True)
    summary: str
    follow_up_tasks: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    risk_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    structured_payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    review_status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    reviewer_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    provider: str = Field(default="mock", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditEventRecord(SQLModel, table=True):
    __tablename__ = "audit_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    action: str = Field(max_length=100, index=True)
    entity_type: str = Field(default="", max_length=50)
    entity_id: Optional[str] = Field(default=None, max_length=64)
    synthetic_only: bool = Field(default=True)
    metadata_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApprovedContentChunk(SQLModel, table=True):
    __tablename__ = "approved_content_chunks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    chunk_id: str = Field(max_length=100, index=True)
    title: str = Field(max_length=200)
    source: str = Field(max_length=200)
    content: str
    language: str = Field(default="en", max_length=10, index=True)
    embedding: list[float] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthQuestion(SQLModel, table=True):
    __tablename__ = "health_questions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    question_text: str
    language: str = Field(default="en", max_length=10)
    worker_id: str = Field(default="synthetic-worker-001", max_length=50)
    approved_content_only: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AIAnswer(SQLModel, table=True):
    __tablename__ = "ai_answers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    question_id: UUID = Field(foreign_key="health_questions.id", index=True)
    answer_text: str
    citations: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    risk_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    hallucination_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    refused: bool = Field(default=False)
    refusal_reason: Optional[str] = Field(default=None, max_length=500)
    review_status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    reviewer_comment: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    retrieval_scores: list[float] = Field(default_factory=list, sa_column=Column(JSON))
    approved_content_only: bool = Field(default=True)
    provider: str = Field(default="mock", max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvaluationRun(SQLModel, table=True):
    __tablename__ = "evaluation_runs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    total_questions: int = Field(default=0)
    answered: int = Field(default=0)
    refused: int = Field(default=0)
    with_citations: int = Field(default=0)
    avg_retrieval_score: float = Field(default=0.0)
    results: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
