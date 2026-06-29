from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from app.core.config import Settings
from app.db.models import AuditEventRecord
from app.models.schemas import AuditEvent


class AuditLogger:
    def __init__(self, settings: Settings, session: Session | None = None) -> None:
        self.settings = settings
        self.session = session

    def record(
        self,
        event: AuditEvent,
        *,
        entity_type: str = "",
        entity_id: str | None = None,
    ) -> None:
        if self.session is not None and self.settings.database_url:
            record = AuditEventRecord(
                action=event.action,
                entity_type=entity_type,
                entity_id=entity_id,
                synthetic_only=event.synthetic_only,
                metadata_json=event.metadata,
                created_at=event.created_at,
            )
            self.session.add(record)
            self.session.commit()
            return

        import json

        payload = event.model_dump(mode="json")
        self.settings.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings.audit_log_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(payload, sort_keys=True) + "\n")

    def list_events(
        self,
        session: Session,
        *,
        action: str | None = None,
        limit: int = 50,
    ) -> list[AuditEventRecord]:
        statement = select(AuditEventRecord).order_by(AuditEventRecord.created_at.desc()).limit(limit)
        if action:
            statement = (
                select(AuditEventRecord)
                .where(AuditEventRecord.action == action)
                .order_by(AuditEventRecord.created_at.desc())
                .limit(limit)
            )
        return list(session.exec(statement).all())
