import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from app.core.config import Settings, get_settings
from app.data.evaluation_cases import GOLDEN_EVAL_CASES
from app.db.models import AIAnswer, EvaluationRun, HealthQuestion, ReviewStatus
from app.db.session import get_session
from app.models.schemas import (
    AnswerResponse,
    AuditEvent,
    Citation,
    EvaluationCaseResult,
    EvaluationResult,
    QADashboardSummary,
    QuestionCreateInput,
    QuestionDetailResponse,
    QuestionResponse,
    ReviewInput,
)
from app.services.audit import AuditLogger
from app.services.llm import get_llm_provider
from app.services.rag import VectorRetriever
from app.services.safety import assess_question, assess_retrieval

logger = logging.getLogger(__name__)

router = APIRouter()


def get_audit_logger(
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> AuditLogger:
    return AuditLogger(settings=settings, session=session)


def _question_response(question: HealthQuestion) -> QuestionResponse:
    return QuestionResponse(
        id=question.id,
        question_text=question.question_text,
        language=question.language,
        worker_id=question.worker_id,
        approved_content_only=question.approved_content_only,
        created_at=question.created_at,
    )


def _answer_response(answer: AIAnswer) -> AnswerResponse:
    citations = [Citation(**item) for item in answer.citations]
    return AnswerResponse(
        id=answer.id,
        question_id=answer.question_id,
        answer_text=answer.answer_text,
        citations=citations,
        risk_flags=answer.risk_flags,
        hallucination_flags=answer.hallucination_flags,
        refused=answer.refused,
        refusal_reason=answer.refusal_reason,
        review_status=answer.review_status.value,
        reviewer_comment=answer.reviewer_comment,
        reviewed_at=answer.reviewed_at,
        retrieval_scores=answer.retrieval_scores,
        approved_content_only=answer.approved_content_only,
        provider=answer.provider,
        created_at=answer.created_at,
    )


@router.post("/questions", response_model=QuestionResponse)
def create_question(
    payload: QuestionCreateInput,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> QuestionResponse:
    question = HealthQuestion(
        question_text=payload.question_text,
        language=payload.language,
        worker_id=payload.worker_id,
        approved_content_only=payload.approved_content_only,
    )
    session.add(question)
    session.commit()
    session.refresh(question)
    audit_logger.record(
        AuditEvent(
            action="qa.question.create",
            metadata={"language": question.language, "worker_id": question.worker_id},
        ),
        entity_type="health_question",
        entity_id=str(question.id),
    )
    return _question_response(question)


@router.get("/questions", response_model=list[QuestionDetailResponse])
def list_questions(session: Session = Depends(get_session)) -> list[QuestionDetailResponse]:
    questions = session.exec(
        select(HealthQuestion).order_by(HealthQuestion.created_at.desc())
    ).all()
    results: list[QuestionDetailResponse] = []
    for question in questions:
        answer = session.exec(
            select(AIAnswer)
            .where(AIAnswer.question_id == question.id)
            .order_by(AIAnswer.created_at.desc())
        ).first()
        results.append(
            QuestionDetailResponse(
                question=_question_response(question),
                latest_answer=_answer_response(answer) if answer else None,
            )
        )
    return results


@router.get("/questions/{question_id}", response_model=QuestionDetailResponse)
def get_question(question_id: UUID, session: Session = Depends(get_session)) -> QuestionDetailResponse:
    question = session.get(HealthQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = session.exec(
        select(AIAnswer)
        .where(AIAnswer.question_id == question_id)
        .order_by(AIAnswer.created_at.desc())
    ).first()
    return QuestionDetailResponse(
        question=_question_response(question),
        latest_answer=_answer_response(answer) if answer else None,
    )


@router.post("/questions/{question_id}/answer", response_model=AnswerResponse)
def answer_question(
    question_id: UUID,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    settings: Settings = Depends(get_settings),
) -> AnswerResponse:
    question = session.get(HealthQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    provider = get_llm_provider()
    provider_name = "openai" if provider.__class__.__name__ == "OpenAICompatibleProvider" else "mock"

    question_safety = assess_question(question.question_text, question.language)
    if question_safety.refused:
        answer = AIAnswer(
            question_id=question.id,
            answer_text=(
                "This question cannot be answered safely in this demo. "
                "Please escalate to a supervising clinician or emergency services if urgent."
            ),
            citations=[],
            risk_flags=question_safety.risk_flags,
            hallucination_flags=question_safety.hallucination_flags,
            refused=True,
            refusal_reason=question_safety.refusal_reason,
            review_status=ReviewStatus.PENDING,
            retrieval_scores=[],
            approved_content_only=question.approved_content_only,
            provider=provider_name,
        )
        session.add(answer)
        session.commit()
        session.refresh(answer)
        audit_logger.record(
            AuditEvent(
                action="qa.answer",
                metadata={
                    "provider": provider_name,
                    "refused": True,
                    "refusal_reason": answer.refusal_reason,
                    "citation_count": 0,
                    "risk_flags": answer.risk_flags,
                },
            ),
            entity_type="ai_answer",
            entity_id=str(answer.id),
        )
        return _answer_response(answer)

    retriever = VectorRetriever(session)
    search_language = question.language if question.language in {"en", "am"} else None
    search_result = retriever.search(
        question.question_text,
        limit=settings.retrieval_top_k,
        language=search_language,
        min_score=0.0,
    )
    retrieval_safety = assess_retrieval(
        search_result.matches,
        approved_content_only=question.approved_content_only,
    )

    if retrieval_safety.refused:
        answer = AIAnswer(
            question_id=question.id,
            answer_text=(
                "No sufficiently matching approved content was found. "
                "Please consult a supervising clinician."
            ),
            citations=[],
            risk_flags=retrieval_safety.risk_flags,
            hallucination_flags=retrieval_safety.hallucination_flags,
            refused=True,
            refusal_reason=retrieval_safety.refusal_reason,
            review_status=ReviewStatus.PENDING,
            retrieval_scores=[m.score for m in search_result.matches],
            approved_content_only=question.approved_content_only,
            provider=provider_name,
        )
        session.add(answer)
        session.commit()
        session.refresh(answer)
        audit_logger.record(
            AuditEvent(
                action="qa.answer",
                metadata={
                    "provider": provider_name,
                    "refused": True,
                    "refusal_reason": answer.refusal_reason,
                    "citation_count": 0,
                    "risk_flags": answer.risk_flags,
                },
            ),
            entity_type="ai_answer",
            entity_id=str(answer.id),
        )
        return _answer_response(answer)

    llm_result = provider.answer_question(
        question.question_text,
        question.language,
        search_result.matches,
        approved_content_only=question.approved_content_only,
    )

    risk_flags = list(dict.fromkeys(question_safety.risk_flags + llm_result.get("risk_flags", [])))
    hallucination_flags = list(
        dict.fromkeys(retrieval_safety.hallucination_flags + llm_result.get("hallucination_flags", []))
    )

    answer = AIAnswer(
        question_id=question.id,
        answer_text=llm_result.get("answer_text", ""),
        citations=llm_result.get("citations", []),
        risk_flags=risk_flags,
        hallucination_flags=hallucination_flags,
        refused=bool(llm_result.get("refused", False)),
        refusal_reason=llm_result.get("refusal_reason"),
        review_status=ReviewStatus.PENDING,
        retrieval_scores=[m.score for m in search_result.matches],
        approved_content_only=question.approved_content_only,
        provider=provider_name,
    )
    session.add(answer)
    session.commit()
    session.refresh(answer)
    audit_logger.record(
        AuditEvent(
            action="qa.answer",
            metadata={
                "provider": provider_name,
                "refused": answer.refused,
                "refusal_reason": answer.refusal_reason,
                "citation_count": len(answer.citations),
                "risk_flags": answer.risk_flags,
                "hallucination_flags": answer.hallucination_flags,
            },
        ),
        entity_type="ai_answer",
        entity_id=str(answer.id),
    )
    logger.info(
        "qa answer generated question_id=%s answer_id=%s refused=%s",
        question.id,
        answer.id,
        answer.refused,
    )
    return _answer_response(answer)


@router.post("/answers/{answer_id}/review", response_model=AnswerResponse)
def review_answer(
    answer_id: UUID,
    payload: ReviewInput,
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
) -> AnswerResponse:
    answer = session.get(AIAnswer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    status_map = {
        "approve": ReviewStatus.APPROVED,
        "reject": ReviewStatus.REJECTED,
        "request_changes": ReviewStatus.CHANGES_REQUESTED,
    }
    answer.review_status = status_map[payload.action.value]
    answer.reviewer_comment = payload.reviewer_comment
    answer.reviewed_at = datetime.now(UTC)
    session.add(answer)
    session.commit()
    session.refresh(answer)
    audit_logger.record(
        AuditEvent(
            action="qa.answer.review",
            metadata={
                "review_status": answer.review_status.value,
                "comment": payload.reviewer_comment,
            },
        ),
        entity_type="ai_answer",
        entity_id=str(answer.id),
    )
    return _answer_response(answer)


@router.get("/dashboard/qa-summary", response_model=QADashboardSummary)
def qa_dashboard_summary(session: Session = Depends(get_session)) -> QADashboardSummary:
    total_questions = session.exec(select(func.count()).select_from(HealthQuestion)).one()
    total_answers = session.exec(select(func.count()).select_from(AIAnswer)).one()
    pending = session.exec(
        select(func.count()).select_from(AIAnswer).where(AIAnswer.review_status == ReviewStatus.PENDING)
    ).one()
    approved = session.exec(
        select(func.count()).select_from(AIAnswer).where(AIAnswer.review_status == ReviewStatus.APPROVED)
    ).one()
    rejected = session.exec(
        select(func.count()).select_from(AIAnswer).where(AIAnswer.review_status == ReviewStatus.REJECTED)
    ).one()
    changes = session.exec(
        select(func.count())
        .select_from(AIAnswer)
        .where(AIAnswer.review_status == ReviewStatus.CHANGES_REQUESTED)
    ).one()
    refused = session.exec(
        select(func.count()).select_from(AIAnswer).where(AIAnswer.refused.is_(True))
    ).one()
    return QADashboardSummary(
        pending_review=pending,
        approved=approved,
        rejected=rejected,
        changes_requested=changes,
        total_questions=total_questions,
        total_answers=total_answers,
        refused_answers=refused,
    )


@router.post("/evaluation/run", response_model=EvaluationResult)
def run_evaluation(
    session: Session = Depends(get_session),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    settings: Settings = Depends(get_settings),
) -> EvaluationResult:
    provider = get_llm_provider()
    provider_name = "openai" if provider.__class__.__name__ == "OpenAICompatibleProvider" else "mock"
    retriever = VectorRetriever(session)

    results: list[EvaluationCaseResult] = []
    answered = 0
    refused = 0
    with_citations = 0
    score_total = 0.0
    score_count = 0

    for case in GOLDEN_EVAL_CASES:
        question_safety = assess_question(case["question"], case["language"])
        if question_safety.refused or case.get("expect_refusal"):
            refused += 1
            results.append(
                EvaluationCaseResult(
                    question=case["question"],
                    language=case["language"],
                    expected_topic=case.get("expected_topic") or "refusal",
                    answered=False,
                    refused=True,
                    has_citations=False,
                    top_score=0.0,
                    matched_topic=None,
                )
            )
            continue

        search_language = case["language"] if case["language"] in {"en", "am"} else None
        search_result = retriever.search(
            case["question"],
            limit=settings.retrieval_top_k,
            language=search_language,
            min_score=0.0,
        )
        top_score = search_result.matches[0].score if search_result.matches else 0.0
        matched_topic = search_result.matches[0].id if search_result.matches else None
        if top_score > 0:
            score_total += top_score
            score_count += 1

        retrieval_safety = assess_retrieval(
            search_result.matches,
            approved_content_only=True,
        )
        if retrieval_safety.refused:
            refused += 1
            results.append(
                EvaluationCaseResult(
                    question=case["question"],
                    language=case["language"],
                    expected_topic=case.get("expected_topic") or "",
                    answered=False,
                    refused=True,
                    has_citations=False,
                    top_score=top_score,
                    matched_topic=matched_topic,
                )
            )
            continue

        llm_result = provider.answer_question(
            case["question"],
            case["language"],
            search_result.matches,
            approved_content_only=True,
        )
        has_citations = bool(llm_result.get("citations"))
        is_refused = bool(llm_result.get("refused", False))
        if is_refused:
            refused += 1
        else:
            answered += 1
        if has_citations:
            with_citations += 1

        results.append(
            EvaluationCaseResult(
                question=case["question"],
                language=case["language"],
                expected_topic=case.get("expected_topic") or "",
                answered=not is_refused,
                refused=is_refused,
                has_citations=has_citations,
                top_score=top_score,
                matched_topic=matched_topic,
            )
        )

    total = len(GOLDEN_EVAL_CASES)
    avg_score = round(score_total / score_count, 3) if score_count else 0.0
    eval_result = EvaluationResult(
        total_questions=total,
        answered=answered,
        refused=refused,
        with_citations=with_citations,
        citation_rate=round(with_citations / total, 3) if total else 0.0,
        refusal_rate=round(refused / total, 3) if total else 0.0,
        avg_retrieval_score=avg_score,
        results=results,
    )

    run = EvaluationRun(
        total_questions=total,
        answered=answered,
        refused=refused,
        with_citations=with_citations,
        avg_retrieval_score=avg_score,
        results=[item.model_dump() for item in results],
    )
    session.add(run)
    session.commit()

    audit_logger.record(
        AuditEvent(
            action="evaluation.run",
            metadata={
                "provider": provider_name,
                "total_questions": total,
                "answered": answered,
                "refused": refused,
                "with_citations": with_citations,
            },
        ),
        entity_type="evaluation_run",
        entity_id=str(run.id),
    )
    return eval_result
