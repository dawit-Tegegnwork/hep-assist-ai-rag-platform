from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from app.core.config import Settings, get_settings
from app.db.models import ClinicalNote, Extraction, ReviewStatus
from app.db.session import get_session
from app.models.schemas import (
    AuditEvent,
    AuditEventResponse,
    DashboardSummary,
    ExtractionResponse,
    NoteCreateInput,
    NoteDetailResponse,
    NoteResponse,
    ReviewInput,
)
from app.services.audit import AuditLogger
from app.services.llm import get_llm_provider

router = APIRouter()


def get_audit_logger(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> AuditLogger:
    return AuditLogger(settings=settings, session=session)


def _note_response(note: ClinicalNote) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        raw_text=note.raw_text,
        note_type=note.note_type,
        created_at=note.created_at,
    )


def _extraction_response(extraction: Extraction) -> ExtractionResponse:
    return ExtractionResponse(
        id=extraction.id,
        note_id=extraction.note_id,
        summary=extraction.summary,
        follow_up_tasks=extraction.follow_up_tasks,
        risk_flags=extraction.risk_flags,
        structured_payload=extraction.structured_payload,
        review_status=extraction.review_status.value,
        reviewer_comment=extraction.reviewer_comment,
        reviewed_at=extraction.reviewed_at,
        provider=extraction.provider,
        created_at=extraction.created_at,
    )


@router.post("/notes", response_model=NoteResponse)
def create_note(
    payload: NoteCreateInput,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> NoteResponse:
    note = ClinicalNote(title=payload.title, raw_text=payload.raw_text, note_type=payload.note_type)
    session.add(note)
    session.commit()
    session.refresh(note)
    audit_logger.record(
        AuditEvent(action="note.create", metadata={"title": note.title, "note_type": note.note_type}),
        entity_type="clinical_note",
        entity_id=str(note.id),
    )
    return _note_response(note)


@router.get("/notes/{note_id}", response_model=NoteDetailResponse)
def get_note(note_id: UUID, session: Session = Depends(get_session)) -> NoteDetailResponse:
    note = session.get(ClinicalNote, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    extraction = session.exec(
        select(Extraction)
        .where(Extraction.note_id == note_id)
        .order_by(Extraction.created_at.desc())
    ).first()

    return NoteDetailResponse(
        note=_note_response(note),
        latest_extraction=_extraction_response(extraction) if extraction else None,
    )


@router.post("/notes/{note_id}/extract", response_model=ExtractionResponse)
def extract_note(
    note_id: UUID,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ExtractionResponse:
    note = session.get(ClinicalNote, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    provider = get_llm_provider()
    provider_name = "openai" if provider.__class__.__name__ == "OpenAICompatibleProvider" else "mock"
    result = provider.extract(note.raw_text, note.note_type)

    extraction = Extraction(
        note_id=note.id,
        summary=result["summary"],
        follow_up_tasks=result.get("follow_up_tasks", []),
        risk_flags=result.get("risk_flags", []),
        structured_payload=result.get("structured_payload", {}),
        review_status=ReviewStatus.PENDING,
        provider=provider_name,
    )
    session.add(extraction)
    session.commit()
    session.refresh(extraction)
    audit_logger.record(
        AuditEvent(
            action="extraction.run",
            metadata={"provider": provider_name, "risk_flags": extraction.risk_flags},
        ),
        entity_type="extraction",
        entity_id=str(extraction.id),
    )
    return _extraction_response(extraction)


@router.post("/extractions/{extraction_id}/review", response_model=ExtractionResponse)
def review_extraction(
    extraction_id: UUID,
    payload: ReviewInput,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ExtractionResponse:
    extraction = session.get(Extraction, extraction_id)
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    status_map = {
        "approve": ReviewStatus.APPROVED,
        "reject": ReviewStatus.REJECTED,
        "request_changes": ReviewStatus.CHANGES_REQUESTED,
    }
    extraction.review_status = status_map[payload.action.value]
    extraction.reviewer_comment = payload.reviewer_comment
    extraction.reviewed_at = datetime.now(UTC)
    session.add(extraction)
    session.commit()
    session.refresh(extraction)
    audit_logger.record(
        AuditEvent(
            action="extraction.review",
            metadata={"review_status": extraction.review_status.value, "comment": payload.reviewer_comment},
        ),
        entity_type="extraction",
        entity_id=str(extraction.id),
    )
    return _extraction_response(extraction)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(session: Session = Depends(get_session)) -> DashboardSummary:
    total_notes = session.exec(select(func.count()).select_from(ClinicalNote)).one()
    total_extractions = session.exec(select(func.count()).select_from(Extraction)).one()
    pending = session.exec(
        select(func.count()).select_from(Extraction).where(Extraction.review_status == ReviewStatus.PENDING)
    ).one()
    approved = session.exec(
        select(func.count()).select_from(Extraction).where(Extraction.review_status == ReviewStatus.APPROVED)
    ).one()
    rejected = session.exec(
        select(func.count()).select_from(Extraction).where(Extraction.review_status == ReviewStatus.REJECTED)
    ).one()
    changes = session.exec(
        select(func.count())
        .select_from(Extraction)
        .where(Extraction.review_status == ReviewStatus.CHANGES_REQUESTED)
    ).one()
    return DashboardSummary(
        pending_review=pending,
        approved=approved,
        rejected=rejected,
        changes_requested=changes,
        total_notes=total_notes,
        total_extractions=total_extractions,
    )


@router.get("/audit", response_model=list[AuditEventResponse])
def list_audit_events(
    action: str | None = None,
    limit: int = 50,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> list[AuditEventResponse]:
    audit_logger = AuditLogger(settings=settings, session=session)
    events = audit_logger.list_events(session, action=action, limit=min(limit, 200))
    return [
        AuditEventResponse(
            id=e.id,
            action=e.action,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            synthetic_only=e.synthetic_only,
            metadata=e.metadata_json,
            created_at=e.created_at,
        )
        for e in events
    ]
