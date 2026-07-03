from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.interop.adapters import adapt_payload
from app.interop.audit import InteropAuditLogger
from app.interop.db_models import InteropAuditEvent, InteropMessage
from app.interop.schemas import (
    AuditEventOut,
    CanonicalBundle,
    DashboardStats,
    ExportResponse,
    IngestResponse,
    InteropSource,
    MessageStatus,
    ValidationErrorDetail,
    ValidationStatus,
)
from app.interop.validators import extract_external_id, validate_payload


class DuplicateMessageError(Exception):
    def __init__(self, external_id: str, source: InteropSource) -> None:
        self.external_id = external_id
        self.source = source
        super().__init__(f"Duplicate message for {source.value}:{external_id}")


class InteropService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = InteropAuditLogger(session)

    def ingest(self, source: InteropSource, payload: dict) -> IngestResponse:
        external_id = extract_external_id(source, payload)
        message = InteropMessage(
            source=source.value,
            external_id=external_id,
            status=MessageStatus.RECEIVED.value,
            raw_payload=payload,
        )
        self.session.add(message)
        try:
            self.session.commit()
            self.session.refresh(message)
        except IntegrityError as exc:
            self.session.rollback()
            self.audit.record(
                "payload_received",
                source=source,
                status="duplicate_rejected",
                details={"external_id": external_id, "error": "duplicate_id"},
            )
            raise DuplicateMessageError(external_id, source) from exc

        self.audit.record(
            "payload_received",
            message_id=message.id,
            source=source,
            status=MessageStatus.RECEIVED.value,
            details={"external_id": external_id},
        )

        errors = validate_payload(source, payload)
        if errors:
            message.validation_status = ValidationStatus.FAILED.value
            message.status = MessageStatus.VALIDATION_FAILED.value
            message.validation_errors = [e.model_dump() for e in errors]
            message.updated_at = datetime.now(UTC)
            self.session.add(message)
            self.session.commit()
            self.audit.record(
                "validation_failed",
                message_id=message.id,
                source=source,
                status=ValidationStatus.FAILED.value,
                details={"errors": message.validation_errors},
            )
            return IngestResponse(
                message_id=message.id,
                source=source,
                status=MessageStatus.VALIDATION_FAILED,
                validation_status=ValidationStatus.FAILED,
                validation_errors=errors,
            )

        message.validation_status = ValidationStatus.PASSED.value
        message.status = MessageStatus.VALIDATED.value
        message.validation_errors = []
        message.updated_at = datetime.now(UTC)
        self.session.add(message)
        self.session.commit()
        self.audit.record(
            "validation_passed",
            message_id=message.id,
            source=source,
            status=ValidationStatus.PASSED.value,
        )

        canonical = adapt_payload(source, payload, str(message.id))
        message.canonical_payload = canonical.model_dump()
        message.status = MessageStatus.TRANSFORMED.value
        message.updated_at = datetime.now(UTC)
        self.session.add(message)
        self.session.commit()
        self.audit.record(
            "transformed",
            message_id=message.id,
            source=source,
            status=MessageStatus.TRANSFORMED.value,
            details={"canonical_keys": list(canonical.model_dump().keys())},
        )

        return IngestResponse(
            message_id=message.id,
            source=source,
            status=MessageStatus.TRANSFORMED,
            validation_status=ValidationStatus.PASSED,
            canonical_preview=canonical,
        )

    def export_message(self, message_id: UUID, export_format: str = "canonical-json") -> ExportResponse:
        message = self.session.get(InteropMessage, message_id)
        if message is None:
            raise KeyError(f"Message {message_id} not found")
        if message.validation_status != ValidationStatus.PASSED.value:
            raise ValueError("Cannot export message that failed validation")
        if not message.canonical_payload:
            raise ValueError("Message has no canonical payload")

        export_payload = {
            "format": export_format,
            "source": message.source,
            "external_id": message.external_id,
            "exported_at": datetime.now(UTC).isoformat(),
            "synthetic_only": True,
            "canonical": message.canonical_payload,
        }
        message.exported = True
        message.status = MessageStatus.EXPORTED.value
        message.updated_at = datetime.now(UTC)
        self.session.add(message)
        self.session.commit()
        self.audit.record(
            "exported",
            message_id=message.id,
            source=message.source,
            status=MessageStatus.EXPORTED.value,
            details={"export_format": export_format},
        )
        return ExportResponse(
            message_id=message.id,
            export_format=export_format,
            payload=export_payload,
            exported_at=datetime.now(UTC),
        )

    def dashboard_stats(self) -> DashboardStats:
        messages = list(self.session.exec(select(InteropMessage)).all())
        events = self.audit.list_events(limit=10)
        by_source: dict[str, int] = {}
        for msg in messages:
            by_source[msg.source] = by_source.get(msg.source, 0) + 1
        return DashboardStats(
            total_messages=len(messages),
            failed_validations=sum(1 for m in messages if m.validation_status == ValidationStatus.FAILED.value),
            successful_exports=sum(1 for m in messages if m.exported),
            by_source=by_source,
            latest_events=[
                {
                    "id": str(e.id),
                    "action": e.action,
                    "source": e.source,
                    "status": e.status,
                    "message_id": str(e.message_id) if e.message_id else None,
                    "created_at": e.created_at.isoformat(),
                }
                for e in events
            ],
        )

    def list_audit_events(self, limit: int = 50) -> list[AuditEventOut]:
        events = self.audit.list_events(limit=limit)
        return [
            AuditEventOut(
                id=e.id,
                message_id=e.message_id,
                action=e.action,
                source=e.source,
                status=e.status,
                details=e.details,
                created_at=e.created_at,
            )
            for e in events
        ]

    def get_message(self, message_id: UUID) -> InteropMessage | None:
        return self.session.get(InteropMessage, message_id)

    def get_canonical(self, message_id: UUID) -> CanonicalBundle | None:
        message = self.get_message(message_id)
        if message and message.canonical_payload:
            return CanonicalBundle.model_validate(message.canonical_payload)
        return None
