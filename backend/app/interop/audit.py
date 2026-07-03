from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from app.interop.db_models import InteropAuditEvent, InteropMessage
from app.interop.schemas import InteropSource


class InteropAuditLogger:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(
        self,
        action: str,
        *,
        message_id: UUID | None = None,
        source: InteropSource | str | None = None,
        status: str | None = None,
        details: dict | None = None,
    ) -> InteropAuditEvent:
        event = InteropAuditEvent(
            message_id=message_id,
            action=action,
            source=source.value if isinstance(source, InteropSource) else source,
            status=status,
            details=details or {},
            synthetic_only=True,
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_events(self, *, limit: int = 50) -> list[InteropAuditEvent]:
        statement = select(InteropAuditEvent).order_by(InteropAuditEvent.created_at.desc()).limit(limit)
        return list(self.session.exec(statement).all())


def count_messages(session: Session) -> int:
    return len(list(session.exec(select(InteropMessage)).all()))
