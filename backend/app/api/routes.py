from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.models.schemas import (
    AuditEvent,
    ClinicalPreprocessInput,
    ClinicalPreprocessOutput,
    GuidelineSearchInput,
    GuidelineSearchOutput,
    SoapNoteInput,
    SoapNoteOutput,
)
from app.services.audit import AuditLogger
from app.services.preprocessing import preprocess_clinical_text
from app.services.rag import GuidelineRetriever
from app.services.soap import build_soap_note

router = APIRouter()


def get_audit_logger(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> AuditLogger:
    return AuditLogger(settings=settings, session=session)


@router.post("/clinical/preprocess", response_model=ClinicalPreprocessOutput)
def preprocess_endpoint(
    payload: ClinicalPreprocessInput,
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ClinicalPreprocessOutput:
    result = preprocess_clinical_text(payload.text)
    audit_logger.record(
        AuditEvent(
            action="clinical.preprocess",
            synthetic_only=True,
            metadata={"redactions": result.redactions, "token_count": result.token_count},
        )
    )
    return result


@router.post("/guidelines/search", response_model=GuidelineSearchOutput)
def guideline_search_endpoint(
    payload: GuidelineSearchInput,
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> GuidelineSearchOutput:
    result = GuidelineRetriever().search(payload.query, limit=payload.limit)
    audit_logger.record(
        AuditEvent(
            action="guidelines.search",
            synthetic_only=True,
            metadata={"query": payload.query, "match_count": len(result.matches)},
        )
    )
    return result


@router.post("/soap-note", response_model=SoapNoteOutput)
def soap_note_endpoint(
    payload: SoapNoteInput,
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> SoapNoteOutput:
    result = build_soap_note(payload)
    audit_logger.record(
        AuditEvent(
            action="soap_note.create",
            synthetic_only=True,
            metadata={"problems": payload.problems, "source": "synthetic-demo"},
        )
    )
    return result

