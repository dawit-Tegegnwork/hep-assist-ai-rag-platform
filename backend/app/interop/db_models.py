from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.interop.schemas import InteropSource, MessageStatus, ValidationStatus


class InteropMessage(SQLModel, table=True):
    __tablename__ = "interop_messages"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_interop_source_external_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source: str = Field(max_length=20, index=True)
    external_id: str = Field(max_length=128, index=True)
    status: str = Field(default=MessageStatus.RECEIVED.value, max_length=32)
    validation_status: str = Field(default=ValidationStatus.FAILED.value, max_length=16)
    validation_errors: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    raw_payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    canonical_payload: dict | None = Field(default=None, sa_column=Column(JSON))
    exported: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InteropAuditEvent(SQLModel, table=True):
    __tablename__ = "interop_audit_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID | None = Field(default=None, index=True)
    action: str = Field(max_length=64, index=True)
    source: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, max_length=32)
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    synthetic_only: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
