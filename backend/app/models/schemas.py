from datetime import UTC, datetime

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

