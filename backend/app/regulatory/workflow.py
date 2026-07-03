from enum import Enum


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    TECHNICAL_REVIEW = "technical_review"
    CLARIFICATION_REQUESTED = "clarification_requested"
    RESUBMITTED = "resubmitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class TransitionAction(str, Enum):
    START_TECHNICAL_REVIEW = "start_technical_review"
    REQUEST_CLARIFICATION = "request_clarification"
    RESUBMIT = "resubmit"
    APPROVE = "approve"
    REJECT = "reject"


# (current_status, action) -> next_status
TRANSITIONS: dict[tuple[ApplicationStatus, TransitionAction], ApplicationStatus] = {
    (ApplicationStatus.SUBMITTED, TransitionAction.START_TECHNICAL_REVIEW): ApplicationStatus.TECHNICAL_REVIEW,
    (ApplicationStatus.RESUBMITTED, TransitionAction.START_TECHNICAL_REVIEW): ApplicationStatus.TECHNICAL_REVIEW,
    (ApplicationStatus.TECHNICAL_REVIEW, TransitionAction.REQUEST_CLARIFICATION): (
        ApplicationStatus.CLARIFICATION_REQUESTED
    ),
    (ApplicationStatus.TECHNICAL_REVIEW, TransitionAction.APPROVE): ApplicationStatus.APPROVED,
    (ApplicationStatus.TECHNICAL_REVIEW, TransitionAction.REJECT): ApplicationStatus.REJECTED,
    (ApplicationStatus.CLARIFICATION_REQUESTED, TransitionAction.RESUBMIT): ApplicationStatus.RESUBMITTED,
}


ROLE_TRANSITIONS: dict[str, set[TransitionAction]] = {
    "applicant": {TransitionAction.RESUBMIT},
    "technical_reviewer": {
        TransitionAction.START_TECHNICAL_REVIEW,
        TransitionAction.REQUEST_CLARIFICATION,
        TransitionAction.APPROVE,
        TransitionAction.REJECT,
    },
    "admin": set(TransitionAction),
    "auditor": set(),
}


def validate_transition(
    current: ApplicationStatus,
    action: TransitionAction,
    role: str,
) -> ApplicationStatus:
    allowed = ROLE_TRANSITIONS.get(role, set())
    if role != "admin" and action not in allowed:
        raise ValueError(f"Role '{role}' cannot perform '{action.value}'")
    key = (current, action)
    if key not in TRANSITIONS:
        raise ValueError(
            f"Invalid transition: cannot '{action.value}' from status '{current.value}'"
        )
    return TRANSITIONS[key]
