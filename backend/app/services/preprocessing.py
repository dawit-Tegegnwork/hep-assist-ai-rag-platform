import re

from app.models.schemas import ClinicalPreprocessOutput

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d -]{7,}\d)\b")
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")
WHITESPACE_RE = re.compile(r"\s+")

ABBREVIATIONS = {
    "sob": "shortness of breath",
    "hx": "history",
    "htn": "hypertension",
    "dm": "diabetes mellitus",
    "n/v": "nausea and vomiting",
}


def preprocess_clinical_text(text: str) -> ClinicalPreprocessOutput:
    redactions: list[str] = []
    cleaned = text.strip()

    for label, pattern in (
        ("email", EMAIL_RE),
        ("date", DATE_RE),
        ("phone", PHONE_RE),
    ):
        if pattern.search(cleaned):
            redactions.append(label)
            cleaned = pattern.sub(f"[REDACTED_{label.upper()}]", cleaned)

    cleaned = WHITESPACE_RE.sub(" ", cleaned)
    normalized = cleaned.lower()
    for short, expanded in ABBREVIATIONS.items():
        normalized = re.sub(rf"\b{re.escape(short)}\b", expanded, normalized)

    return ClinicalPreprocessOutput(
        original=text,
        cleaned=cleaned,
        normalized=normalized,
        redactions=redactions,
        token_count=len(normalized.split()),
    )
