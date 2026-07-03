from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ApplicationType(str, Enum):
    MARKETING_AUTHORIZATION = "marketing_authorization"
    VARIATION = "variation"
    RENEWAL = "renewal"


class ApplicationCreateInput(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=200)
    application_type: ApplicationType = ApplicationType.MARKETING_AUTHORIZATION
    applicant_organization: str = Field(..., min_length=2, max_length=200)
    dossier_summary: str = Field(..., min_length=10, max_length=4000)
    supporting_documents: list[str] = Field(default_factory=list, max_length=20)


class ApplicationResubmitInput(BaseModel):
    dossier_summary: str = Field(..., min_length=10, max_length=4000)
    supporting_documents: list[str] = Field(default_factory=list, max_length=20)
    applicant_note: str | None = Field(default=None, max_length=2000)


class TransitionInput(BaseModel):
    action: str = Field(..., min_length=3, max_length=50)
    comment: str | None = Field(default=None, max_length=2000)


class ApplicationResponse(BaseModel):
    id: UUID
    reference_number: str
    product_name: str
    application_type: str
    applicant_organization: str
    dossier_summary: str
    supporting_documents: list[str]
    status: str
    submitted_by: str
    assigned_reviewer: str | None
    last_comment: str | None
    created_at: datetime
    updated_at: datetime


class ApplicationDashboardSummary(BaseModel):
    submitted: int
    technical_review: int
    clarification_requested: int
    resubmitted: int
    approved: int
    rejected: int
    total: int
