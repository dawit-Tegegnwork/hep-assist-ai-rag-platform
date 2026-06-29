"""Seed synthetic demo notes for portfolio demos."""

from sqlmodel import Session, select

from app.db.models import ClinicalNote, Extraction, ReviewStatus
from app.db.session import get_engine, init_db
from app.services.llm import MockLLMProvider

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


def seed(force: bool = False) -> int:
    init_db()
    created = 0
    provider = MockLLMProvider()
    with Session(get_engine()) as session:
        existing = session.exec(select(ClinicalNote)).first()
        if existing and not force:
            print("Demo data already exists. Use --force to reseed.")
            return 0

        if force:
            for extraction in session.exec(select(Extraction)).all():
                session.delete(extraction)
            for note in session.exec(select(ClinicalNote)).all():
                session.delete(note)
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
        session.commit()
    print(f"Seeded {created} synthetic notes.")
    return created


if __name__ == "__main__":
    import sys

    seed(force="--force" in sys.argv)
