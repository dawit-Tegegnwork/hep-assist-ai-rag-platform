import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from app.auth.deps import CurrentUser, get_current_user, require_roles
from app.auth.roles import Role
from app.db.models import ApplicationStatus, AuditEventRecord, RegulatoryApplication
from app.db.session import get_session
from app.models.schemas import AuditEvent
from app.regulatory.schemas import (
    ApplicationCreateInput,
    ApplicationDashboardSummary,
    ApplicationResubmitInput,
    ApplicationResponse,
    TransitionInput,
)
from app.regulatory.workflow import TransitionAction, validate_transition
from app.services.audit import AuditLogger
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/regulatory", tags=["regulatory"])


def get_audit_logger(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> AuditLogger:
    return AuditLogger(settings=settings, session=session)


def _next_reference(session: Session) -> str:
    count = session.exec(select(func.count()).select_from(RegulatoryApplication)).one()
    return f"ERIS-DEMO-{count + 1:05d}"


def _to_response(app: RegulatoryApplication) -> ApplicationResponse:
    return ApplicationResponse(
        id=app.id,
        reference_number=app.reference_number,
        product_name=app.product_name,
        application_type=app.application_type,
        applicant_organization=app.applicant_organization,
        dossier_summary=app.dossier_summary,
        supporting_documents=app.supporting_documents,
        status=app.status.value,
        submitted_by=app.submitted_by,
        assigned_reviewer=app.assigned_reviewer,
        last_comment=app.last_comment,
        created_at=app.created_at,
        updated_at=app.updated_at,
    )


def _record_transition_audit(
    audit_logger: AuditLogger,
    application: RegulatoryApplication,
    action: str,
    actor: CurrentUser,
    comment: str | None,
    from_status: str,
    to_status: str,
) -> None:
    audit_logger.record(
        AuditEvent(
            action="regulatory.application.transition",
            metadata={
                "reference_number": application.reference_number,
                "transition_action": action,
                "from_status": from_status,
                "to_status": to_status,
                "actor": actor.username,
                "actor_role": actor.role.value,
                "comment": comment,
            },
        ),
        entity_type="regulatory_application",
        entity_id=str(application.id),
    )


@router.post("/applications", response_model=ApplicationResponse)
def submit_application(
    payload: ApplicationCreateInput,
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(require_roles(Role.APPLICANT, Role.ADMIN)),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ApplicationResponse:
    application = RegulatoryApplication(
        reference_number=_next_reference(session),
        product_name=payload.product_name,
        application_type=payload.application_type.value,
        applicant_organization=payload.applicant_organization,
        dossier_summary=payload.dossier_summary,
        supporting_documents=payload.supporting_documents,
        status=ApplicationStatus.SUBMITTED,
        submitted_by=user.username,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    audit_logger.record(
        AuditEvent(
            action="regulatory.application.submit",
            metadata={
                "reference_number": application.reference_number,
                "product_name": application.product_name,
                "application_type": application.application_type,
                "submitted_by": user.username,
            },
        ),
        entity_type="regulatory_application",
        entity_id=str(application.id),
    )
    logger.info("application submitted ref=%s by=%s", application.reference_number, user.username)
    return _to_response(application)


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
    status: str | None = None,
) -> list[ApplicationResponse]:
    if user.role == Role.APPLICANT:
        statement = (
            select(RegulatoryApplication)
            .where(RegulatoryApplication.submitted_by == user.username)
            .order_by(RegulatoryApplication.created_at.desc())
        )
    else:
        statement = select(RegulatoryApplication).order_by(RegulatoryApplication.created_at.desc())
    if status:
        statement = statement.where(RegulatoryApplication.status == ApplicationStatus(status))
    return [_to_response(a) for a in session.exec(statement).all()]


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ApplicationResponse:
    application = session.get(RegulatoryApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == Role.APPLICANT and application.submitted_by != user.username:
        raise HTTPException(status_code=403, detail="Applicants can only view their own applications")
    return _to_response(application)


@router.post("/applications/{application_id}/transition", response_model=ApplicationResponse)
def transition_application(
    application_id: UUID,
    payload: TransitionInput,
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ApplicationResponse:
    application = session.get(RegulatoryApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == Role.APPLICANT and application.submitted_by != user.username:
        raise HTTPException(status_code=403, detail="Applicants can only act on their own applications")
    if user.role == Role.AUDITOR:
        raise HTTPException(status_code=403, detail="Auditors have read-only access")

    try:
        action = TransitionAction(payload.action)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Unknown action: {payload.action}") from exc

    from_status = application.status.value
    try:
        next_status = validate_transition(application.status, action, user.role.value)
    except ValueError as exc:
        message = str(exc)
        status_code = 403 if "cannot perform" in message else 400
        raise HTTPException(status_code=status_code, detail=message) from exc

    if action == TransitionAction.START_TECHNICAL_REVIEW:
        application.assigned_reviewer = user.username
    if action in {TransitionAction.REQUEST_CLARIFICATION, TransitionAction.APPROVE, TransitionAction.REJECT}:
        application.assigned_reviewer = application.assigned_reviewer or user.username

    application.status = next_status
    application.last_comment = payload.comment
    application.updated_at = datetime.now(UTC)
    session.add(application)
    session.commit()
    session.refresh(application)

    _record_transition_audit(
        audit_logger,
        application,
        action.value,
        user,
        payload.comment,
        from_status,
        next_status.value,
    )
    return _to_response(application)


@router.post("/applications/{application_id}/resubmit", response_model=ApplicationResponse)
def resubmit_application(
    application_id: UUID,
    payload: ApplicationResubmitInput,
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(require_roles(Role.APPLICANT, Role.ADMIN)),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> ApplicationResponse:
    application = session.get(RegulatoryApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == Role.APPLICANT and application.submitted_by != user.username:
        raise HTTPException(status_code=403, detail="Applicants can only resubmit their own applications")
    if application.status != ApplicationStatus.CLARIFICATION_REQUESTED:
        raise HTTPException(
            status_code=400,
            detail="Resubmit is only allowed when clarification has been requested",
        )

    from_status = application.status.value
    application.dossier_summary = payload.dossier_summary
    application.supporting_documents = payload.supporting_documents
    application.status = ApplicationStatus.RESUBMITTED
    application.last_comment = payload.applicant_note
    application.updated_at = datetime.now(UTC)
    session.add(application)
    session.commit()
    session.refresh(application)

    _record_transition_audit(
        audit_logger,
        application,
        TransitionAction.RESUBMIT.value,
        user,
        payload.applicant_note,
        from_status,
        ApplicationStatus.RESUBMITTED.value,
    )
    return _to_response(application)


@router.get("/dashboard/summary", response_model=ApplicationDashboardSummary)
def regulatory_dashboard_summary(
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(
        require_roles(Role.TECHNICAL_REVIEWER, Role.ADMIN, Role.AUDITOR)
    ),
) -> ApplicationDashboardSummary:
    counts = {status.value: 0 for status in ApplicationStatus}
    rows = session.exec(
        select(RegulatoryApplication.status, func.count())
        .group_by(RegulatoryApplication.status)
    ).all()
    for status, count in rows:
        counts[status.value] = count
    total = sum(counts.values())
    return ApplicationDashboardSummary(
        submitted=counts["submitted"],
        technical_review=counts["technical_review"],
        clarification_requested=counts["clarification_requested"],
        resubmitted=counts["resubmitted"],
        approved=counts["approved"],
        rejected=counts["rejected"],
        total=total,
    )


@router.get("/applications/{application_id}/audit", response_model=list[dict])
def application_audit_trail(
    application_id: UUID,
    session: Session = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> list[dict]:
    application = session.get(RegulatoryApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if user.role == Role.APPLICANT and application.submitted_by != user.username:
        raise HTTPException(status_code=403, detail="Access denied")

    events = session.exec(
        select(AuditEventRecord)
        .where(AuditEventRecord.entity_id == str(application_id))
        .order_by(AuditEventRecord.created_at.asc())
    ).all()
    return [
        {
            "id": str(e.id),
            "action": e.action,
            "metadata": e.metadata_json,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
