from sqlalchemy import text
from sqlmodel import Session

from app.core.config import get_settings
from app.db.session import get_engine
from app.services.embeddings import get_embedding_provider


def check_database() -> tuple[bool, str]:
    try:
        with Session(get_engine()) as session:
            session.exec(text("SELECT 1")).one()
        return True, "connected"
    except Exception as exc:
        return False, str(exc)


def build_health_payload(*, detailed: bool = False) -> dict[str, object]:
    settings = get_settings()
    db_ok, db_status = check_database()
    payload: dict[str, object] = {
        "status": "ok" if db_ok else "degraded",
        "service": settings.service_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
    if detailed:
        provider = get_embedding_provider()
        payload["checks"] = {
            "database": {"ok": db_ok, "detail": db_status},
            "embedding_provider": provider.__class__.__name__,
            "llm_provider": "openai" if settings.llm_provider == "openai" else "mock",
        }
    return payload
