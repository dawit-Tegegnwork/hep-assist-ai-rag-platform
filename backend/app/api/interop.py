from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_session
from app.interop.schemas import (
    AuditEventOut,
    DashboardStats,
    ExportResponse,
    IngestResponse,
    InteropSource,
)
from app.interop.service import DuplicateMessageError, InteropService
from app.interop.synthetic_data import SAMPLES, get_sample

router = APIRouter(prefix="/interop", tags=["interop"])


def _service(session: Session = Depends(get_session)) -> InteropService:
    return InteropService(session)


@router.get("/sources")
def list_sources() -> dict[str, object]:
    return {
        "sources": [s.value for s in InteropSource],
        "framing": "Synthetic interoperability adapters inspired by open-source digital health ecosystems.",
    }


@router.get("/samples/{source}")
def sample_payload(source: InteropSource, variant: str = "valid") -> dict:
    try:
        return get_sample(source, variant)
    except KeyError as exc:
        available = list(SAMPLES.get(source, {}).keys())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown variant '{variant}'. Available: {available}",
        ) from exc


@router.post("/ingest/{source}", response_model=IngestResponse)
def ingest_payload(source: InteropSource, payload: dict, service: InteropService = Depends(_service)) -> IngestResponse:
    try:
        return service.ingest(source, payload)
    except DuplicateMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "duplicate_id",
                "message": str(exc),
                "external_id": exc.external_id,
                "source": exc.source.value,
            },
        ) from exc


@router.post("/messages/{message_id}/export", response_model=ExportResponse)
def export_message(
    message_id: UUID,
    export_format: str = "canonical-json",
    service: InteropService = Depends(_service),
) -> ExportResponse:
    try:
        return service.export_message(message_id, export_format=export_format)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(service: InteropService = Depends(_service)) -> DashboardStats:
    return service.dashboard_stats()


@router.get("/audit", response_model=list[AuditEventOut])
def audit_events(limit: int = 50, service: InteropService = Depends(_service)) -> list[AuditEventOut]:
    return service.list_audit_events(limit=min(limit, 200))


@router.get("/messages/{message_id}")
def get_message(message_id: UUID, service: InteropService = Depends(_service)) -> dict:
    message = service.get_message(message_id)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return {
        "id": str(message.id),
        "source": message.source,
        "external_id": message.external_id,
        "status": message.status,
        "validation_status": message.validation_status,
        "validation_errors": message.validation_errors,
        "exported": message.exported,
        "created_at": message.created_at.isoformat(),
        "updated_at": message.updated_at.isoformat(),
    }
