from app.services.safety import assess_answer_grounding, assess_question, assess_retrieval
from app.models.schemas import GuidelineChunk


def test_refuse_emergency_question() -> None:
    result = assess_question("Patient has chest pain and cannot breathe, call 911 now", "en")
    assert result.refused is True
    assert result.refusal_reason == "emergency_or_urgent_care"


def test_refuse_diagnosis_request() -> None:
    result = assess_question("Diagnose whether this patient has hepatitis C", "en")
    assert result.refused is True
    assert result.refusal_reason == "diagnosis_request_not_supported"


def test_refuse_prescribing_request() -> None:
    result = assess_question("Prescribe antiviral dosage for hepatitis C patient", "en")
    assert result.refused is True
    assert result.refusal_reason == "prescribing_request_not_supported"


def test_safe_screening_question_passes() -> None:
    result = assess_question("What screening tests are approved for hepatitis B?", "en")
    assert result.refused is False


def test_low_retrieval_score_refused_in_approved_mode() -> None:
    matches = [
        GuidelineChunk(
            id="x",
            title="Unrelated",
            source="demo",
            summary="unrelated content",
            score=0.1,
            language="en",
        )
    ]
    result = assess_retrieval(matches, approved_content_only=True)
    assert result.refused is True
    assert result.refusal_reason == "low_retrieval_confidence"


def test_hallucination_flag_on_ungrounded_answer() -> None:
    matches = [
        GuidelineChunk(
            id="hep-b",
            title="Hepatitis B Screening",
            source="demo",
            summary="Screen with HBsAg in synthetic scenarios.",
            score=0.8,
            language="en",
        )
    ]
    flags = assess_answer_grounding(
        "The patient should immediately start chemotherapy and experimental surgery tomorrow.",
        matches,
    )
    assert "possible_ungrounded_content" in flags
