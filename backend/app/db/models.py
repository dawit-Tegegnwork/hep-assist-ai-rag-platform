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
