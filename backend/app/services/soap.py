from app.models.schemas import SoapNoteInput, SoapNoteOutput
from app.services.preprocessing import preprocess_clinical_text
from app.services.rag import GuidelineRetriever


def build_soap_note(payload: SoapNoteInput) -> SoapNoteOutput:
    cleaned_history = preprocess_clinical_text(payload.history)
    problems = payload.problems or ["hepatitis risk assessment"]
    guideline_matches = GuidelineRetriever().search(" ".join(problems), limit=2).matches

    objective = "Vitals not provided."
    if payload.vitals:
        objective = "; ".join(f"{key}: {value}" for key, value in sorted(payload.vitals.items()))

    plan = [
        f"Review {match.title.lower()} guidance: {match.summary}"
        for match in guideline_matches
    ]
    plan.append("Use clinician review before applying any generated recommendation.")

    return SoapNoteOutput(
        subjective=f"{payload.chief_complaint}. {cleaned_history.normalized}",
        objective=objective,
        assessment=", ".join(problems),
        plan=plan,
        safety_note=(
            "Escalate urgently for severe abdominal pain, jaundice, confusion, "
            "bleeding, or unstable vital signs."
        ),
    )

