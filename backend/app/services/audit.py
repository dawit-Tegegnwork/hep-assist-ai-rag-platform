import json

from app.core.config import Settings
from app.models.schemas import AuditEvent


class AuditLogger:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def record(self, event: AuditEvent) -> None:
        payload = event.model_dump(mode="json")
        if self.settings.database_url:
            self._record_postgres_ready(payload)
            return
        self.settings.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings.audit_log_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(payload, sort_keys=True) + "\n")

    def _record_postgres_ready(self, payload: dict[str, object]) -> None:
        # Kept dependency-light for the portfolio MVP. The schema is ready for
        # insertion via asyncpg/SQLAlchemy when durable Postgres writes are enabled.
        self.settings.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings.audit_log_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps({"postgres_ready": True, **payload}, sort_keys=True) + "\n")

