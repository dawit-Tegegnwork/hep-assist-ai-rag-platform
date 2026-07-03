"""Seed synthetic demo notes and health-worker Q&A data for portfolio demos."""

from sqlmodel import Session, select

from app.db.models import (
    AIAnswer,
    ApplicationStatus,
    ClinicalNote,
    Extraction,
    HealthQuestion,
    RegulatoryApplication,
    ReviewStatus,
)
from app.db.session import get_engine, init_db
from app.services.llm import MockLLMProvider
from app.services.vector_store import VectorStore

DEMO_NOTES = [
    {
        "title": "Synthetic hepatitis screening follow-up",
        "raw_text": (
            "Synthetic pt reports fatigue and hx of hepatitis exposure. "
            "Prior HCV Ab reactive; needs RNA confirmation pathway review."
        ),
        "note_type": "clinical",
    },
    {
        "title": "Synthetic lab admin note",
        "raw_text": "Lab batch QC review completed. Synthetic specimen IDs only. No patient identifiers stored.",
        "note_type": "lab_admin",
    },
    {
        "title": "Synthetic referral summary",
        "raw_text": "Referral for liver panel and hepatitis screening counseling. Patient phone redacted in source.",
        "note_type": "referral",
    },
    {
        "title": "Synthetic medication review",
        "raw_text": "Reviewed synthetic med list for hepatotoxicity risk flags. Follow-up scheduled in demo workflow.",
        "note_type": "clinical",
    },
    {
        "title": "Synthetic community health visit",
        "raw_text": "Community health worker note: vaccination education provided. No diagnosis documented.",
        "note_type": "community",
    },
]

DEMO_QUESTIONS = [
    {
        "question_text": "What screening tests are approved for hepatitis B in community settings?",
        "language": "en",
        "review_status": ReviewStatus.PENDING,
    },
    {
        "question_text": "How should I refer a patient with abnormal liver panels?",
        "language": "en",
        "review_status": ReviewStatus.APPROVED,
    },
    {
        "question_text": "What triage checklist should I use when connectivity is poor?",
        "language": "en",
        "review_status": ReviewStatus.REJECTED,
    },
    {
        "question_text": "How do I document vaccination education without giving medical advice?",
        "language": "en",
        "review_status": ReviewStatus.PENDING,
    },
    {
        "question_text": "የሂፓታይቲስ B ምርመራ በcommunity setting እንዴት ይደረጋል?",
        "language": "am",
        "review_status": ReviewStatus.PENDING,
    },
    {
        "question_text": "What PPE should health workers use during field visits?",
        "language": "en",
        "review_status": ReviewStatus.APPROVED,
    },
    {
        "question_text": "How should I queue questions when offline?",
        "language": "en",
        "review_status": ReviewStatus.CHANGES_REQUESTED,
    },
    {
        "question_text": "When should I escalate jaundice cases to a clinician?",
        "language": "en",
        "review_status": ReviewStatus.PENDING,
    },
]


DEMO_APPLICATIONS = [
    {
        "reference_number": "ERIS-DEMO-00001",
        "product_name": "Synthetic Antibiotic XR-100",
        "application_type": "marketing_authorization",
        "applicant_organization": "Synthetic Pharma Ltd",
        "dossier_summary": (
            "Initial marketing authorization dossier for XR-100 extended-release tablets. "
            "Includes synthetic stability data and bioequivalence summary for demo review."
        ),
        "supporting_documents": ["module_2.3.pdf", "module_3.2.P.1.pdf"],
        "status": ApplicationStatus.TECHNICAL_REVIEW,
        "submitted_by": "applicant",
        "assigned_reviewer": "reviewer",
    },
    {
        "reference_number": "ERIS-DEMO-00002",
        "product_name": "Synthetic Vaccine Adjuvant V-22",
        "application_type": "variation",
        "applicant_organization": "Demo Biologics Co",
        "dossier_summary": (
            "Type II variation for manufacturing site change. Clarification requested on "
            "cold-chain validation records."
        ),
        "supporting_documents": ["variation_form.pdf"],
        "status": ApplicationStatus.CLARIFICATION_REQUESTED,
        "submitted_by": "applicant",
        "assigned_reviewer": "reviewer",
        "last_comment": "Provide updated cold-chain validation protocol.",
    },
    {
        "reference_number": "ERIS-DEMO-00003",
        "product_name": "Synthetic Analgesic AP-50",
        "application_type": "renewal",
        "applicant_organization": "Synthetic Pharma Ltd",
        "dossier_summary": "Renewal application with updated pharmacovigilance summary.",
        "supporting_documents": ["pv_summary.pdf"],
        "status": ApplicationStatus.APPROVED,
        "submitted_by": "applicant",
        "assigned_reviewer": "reviewer",
        "last_comment": "Meets renewal criteria for demo purposes.",
    },
]


def _generate_demo_answer(
    provider: MockLLMProvider,
    question: HealthQuestion,
    session: Session,
) -> AIAnswer:
    from app.core.config import get_settings
    from app.services.rag import VectorRetriever
    from app.services.safety import assess_question, assess_retrieval

    question_safety = assess_question(question.question_text, question.language)
    if question_safety.refused:
        return AIAnswer(
            question_id=question.id,
            answer_text="Refused: unsafe question for demo assistant.",
            citations=[],
            risk_flags=question_safety.risk_flags,
            hallucination_flags=[],
            refused=True,
            refusal_reason=question_safety.refusal_reason,
            review_status=ReviewStatus.PENDING,
            retrieval_scores=[],
            approved_content_only=question.approved_content_only,
            provider="mock",
        )

    settings = get_settings()
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
        return AIAnswer(
            question_id=question.id,
            answer_text="No approved content match found.",
            citations=[],
            risk_flags=retrieval_safety.risk_flags,
            hallucination_flags=[],
            refused=True,
            refusal_reason=retrieval_safety.refusal_reason,
            review_status=ReviewStatus.PENDING,
            retrieval_scores=[m.score for m in search_result.matches],
            approved_content_only=question.approved_content_only,
            provider="mock",
        )

    llm_result = provider.answer_question(
        question.question_text,
        question.language,
        search_result.matches,
        approved_content_only=question.approved_content_only,
    )
    return AIAnswer(
        question_id=question.id,
        answer_text=llm_result.get("answer_text", ""),
        citations=llm_result.get("citations", []),
        risk_flags=llm_result.get("risk_flags", []),
        hallucination_flags=llm_result.get("hallucination_flags", []),
        refused=bool(llm_result.get("refused", False)),
        refusal_reason=llm_result.get("refusal_reason"),
        review_status=ReviewStatus.PENDING,
        retrieval_scores=[m.score for m in search_result.matches],
        approved_content_only=question.approved_content_only,
        provider="mock",
    )


def seed(force: bool = False) -> int:
    init_db()
    created = 0
    provider = MockLLMProvider()
    with Session(get_engine()) as session:
        store = VectorStore(session)
        store.index_all(force=force)

        existing = session.exec(select(ClinicalNote)).first()
        if existing and not force:
            print("Demo data already exists. Use --force to reseed.")
            return 0

        if force:
            for answer in session.exec(select(AIAnswer)).all():
                session.delete(answer)
            for question in session.exec(select(HealthQuestion)).all():
                session.delete(question)
            for extraction in session.exec(select(Extraction)).all():
                session.delete(extraction)
            for note in session.exec(select(ClinicalNote)).all():
                session.delete(note)
            for app in session.exec(select(RegulatoryApplication)).all():
                session.delete(app)
            session.commit()

        for index, item in enumerate(DEMO_NOTES):
            note = ClinicalNote(**item)
            session.add(note)
            session.commit()
            session.refresh(note)
            created += 1

            result = provider.extract(note.raw_text, note.note_type)
            status = ReviewStatus.PENDING
            if index == 1:
                status = ReviewStatus.APPROVED
            elif index == 2:
                status = ReviewStatus.REJECTED

            extraction = Extraction(
                note_id=note.id,
                summary=result["summary"],
                follow_up_tasks=result.get("follow_up_tasks", []),
                risk_flags=result.get("risk_flags", []),
                structured_payload=result.get("structured_payload", {}),
                review_status=status,
                provider="mock",
            )
            session.add(extraction)

        for item in DEMO_QUESTIONS:
            data = dict(item)
            review_status = data.pop("review_status")
            question = HealthQuestion(**data)
            session.add(question)
            session.commit()
            session.refresh(question)
            created += 1

            answer = _generate_demo_answer(provider, question, session)
            answer.review_status = review_status
            if review_status != ReviewStatus.PENDING:
                answer.reviewer_comment = "Synthetic seed review state"
            session.add(answer)

        existing_apps = session.exec(select(RegulatoryApplication)).first()
        if not existing_apps or force:
            for item in DEMO_APPLICATIONS:
                data = dict(item)
                application = RegulatoryApplication(**data)
                session.add(application)
                created += 1

        session.commit()
    print(f"Seeded {created} synthetic records (notes + questions + applications).")
    return created


if __name__ == "__main__":
    import sys

    seed(force="--force" in sys.argv)
