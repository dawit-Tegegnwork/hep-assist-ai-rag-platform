import re
from dataclasses import dataclass

from app.core.config import get_settings
from app.models.schemas import GuidelineChunk

EMERGENCY_PATTERNS = [
    r"\b(chest pain|heart attack|stroke|unconscious|not breathing|severe bleeding)\b",
    r"\b(call 911|emergency room now|life threatening)\b",
]

DIAGNOSIS_PATTERNS = [
    r"\b(diagnose|diagnosis|what disease|what condition do i have)\b",
    r"\b(is this cancer|do i have hepatitis|confirm infection)\b",
]

PRESCRIBING_PATTERNS = [
    r"\b(prescribe|dosage|how much.*(take|mg)|start medication)\b",
    r"\b(which drug should|antiviral dose|treatment plan for)\b",
]

UNSAFE_PATTERNS = EMERGENCY_PATTERNS + DIAGNOSIS_PATTERNS + PRESCRIBING_PATTERNS


@dataclass(frozen=True)
class SafetyAssessment:
    refused: bool
    refusal_reason: str | None
    risk_flags: list[str]
    hallucination_flags: list[str]


def assess_question(question: str, language: str) -> SafetyAssessment:
    risk_flags: list[str] = []
    text = question.lower()

    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return SafetyAssessment(
                refused=True,
                refusal_reason="emergency_or_urgent_care",
                risk_flags=["emergency_detected"],
                hallucination_flags=[],
            )

    for pattern in DIAGNOSIS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return SafetyAssessment(
                refused=True,
                refusal_reason="diagnosis_request_not_supported",
                risk_flags=["diagnosis_request"],
                hallucination_flags=[],
            )

    for pattern in PRESCRIBING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return SafetyAssessment(
                refused=True,
                refusal_reason="prescribing_request_not_supported",
                risk_flags=["prescribing_request"],
                hallucination_flags=[],
            )

    if language == "am":
        risk_flags.append("local_language_demo")

    return SafetyAssessment(
        refused=False,
        refusal_reason=None,
        risk_flags=risk_flags,
        hallucination_flags=[],
    )


def assess_retrieval(
    matches: list[GuidelineChunk],
    *,
    approved_content_only: bool,
) -> SafetyAssessment:
    settings = get_settings()
    if not matches:
        if approved_content_only:
            return SafetyAssessment(
                refused=True,
                refusal_reason="no_approved_content_match",
                risk_flags=["insufficient_retrieval"],
                hallucination_flags=[],
            )
        return SafetyAssessment(
            refused=False,
            refusal_reason=None,
            risk_flags=["insufficient_retrieval"],
            hallucination_flags=[],
        )

    top_score = matches[0].score
    if approved_content_only and top_score < settings.retrieval_min_score:
        return SafetyAssessment(
            refused=True,
            refusal_reason="low_retrieval_confidence",
            risk_flags=["low_retrieval_score"],
            hallucination_flags=[],
        )

    return SafetyAssessment(
        refused=False,
        refusal_reason=None,
        risk_flags=[],
        hallucination_flags=[],
    )


def assess_answer_grounding(answer_text: str, matches: list[GuidelineChunk]) -> list[str]:
    if not answer_text or not matches:
        return []

    context = " ".join(f"{m.title} {m.summary}" for m in matches).lower()
    answer_terms = {t for t in re.findall(r"[a-z0-9]+", answer_text.lower()) if len(t) > 4}
    context_terms = {t for t in re.findall(r"[a-z0-9]+", context) if len(t) > 4}
    if not answer_terms:
        return []

    unsupported = [term for term in answer_terms if term not in context_terms]
    if len(unsupported) > max(3, len(answer_terms) // 3):
        return ["possible_ungrounded_content"]
    return []
