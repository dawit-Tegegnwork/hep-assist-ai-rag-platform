from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class InteropSource(str, Enum):
    OPENMRS = "openmrs"
    OPENELIS = "openelis"
    DHIS2 = "dhis2"
    FHIR = "fhir"


class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


class MessageStatus(str, Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    VALIDATION_FAILED = "validation_failed"
    TRANSFORMED = "transformed"
    EXPORTED = "exported"


class ValidationErrorDetail(BaseModel):
    field: str
    code: str
    message: str


class CanonicalPatient(BaseModel):
    external_id: str
    source_system: str
    given_name: str
    family_name: str
    birth_date: str | None = None
    gender: str | None = None
    identifiers: list[dict[str, str]] = Field(default_factory=list)


class CanonicalEncounter(BaseModel):
    external_id: str
    patient_external_id: str
    encounter_type: str | None = None
    encounter_datetime: str | None = None
    observations: list[dict[str, Any]] = Field(default_factory=list)


class CanonicalLabResult(BaseModel):
    accession_number: str
    patient_external_id: str
    test_code: str
    test_name: str
    result_value: str
    result_unit: str | None = None
    result_datetime: str | None = None
    status: str = "final"


class CanonicalAggregateReport(BaseModel):
    data_element: str
    org_unit: str
    period: str
    value: float
    category_option_combo: str | None = None


class CanonicalBundle(BaseModel):
    message_id: str
    source: InteropSource
    patients: list[CanonicalPatient] = Field(default_factory=list)
    encounters: list[CanonicalEncounter] = Field(default_factory=list)
    lab_results: list[CanonicalLabResult] = Field(default_factory=list)
    aggregate_reports: list[CanonicalAggregateReport] = Field(default_factory=list)
    fhir_resources: list[dict[str, Any]] = Field(default_factory=list)


class IngestResponse(BaseModel):
    message_id: UUID
    source: InteropSource
    status: MessageStatus
    validation_status: ValidationStatus
    validation_errors: list[ValidationErrorDetail] = Field(default_factory=list)
    canonical_preview: CanonicalBundle | None = None


class ExportResponse(BaseModel):
    message_id: UUID
    export_format: str
    payload: dict[str, Any]
    exported_at: datetime


class DashboardStats(BaseModel):
    total_messages: int
    failed_validations: int
    successful_exports: int
    by_source: dict[str, int]
    latest_events: list[dict[str, Any]]


class AuditEventOut(BaseModel):
    id: UUID
    message_id: UUID | None
    action: str
    source: str | None
    status: str | None
    details: dict[str, Any]
    created_at: datetime
