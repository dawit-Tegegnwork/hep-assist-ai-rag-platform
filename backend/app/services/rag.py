import math
import re
from dataclasses import dataclass
from pathlib import Path

from app.models.schemas import GuidelineChunk, GuidelineSearchOutput

GUIDELINES_PATH = Path(__file__).resolve().parent.parent / "data" / "synthetic_guidelines.md"


@dataclass(frozen=True)
class GuidelineDocument:
    id: str
    title: str
    source: str
    summary: str


def load_guidelines_from_markdown(path: Path = GUIDELINES_PATH) -> list[GuidelineDocument]:
    if not path.exists():
        return _fallback_guidelines()

    text = path.read_text(encoding="utf-8")
    documents: list[GuidelineDocument] = []
    current_title: str | None = None
    summary_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                documents.append(
                    GuidelineDocument(
                        id=_slugify(current_title),
                        title=current_title,
                        source="Synthetic HEP demo guideline v0.1",
                        summary=" ".join(summary_lines).strip(),
                    )
                )
            current_title = line[3:].strip()
            summary_lines = []
            continue
        if current_title and line.strip() and not line.startswith("#"):
            summary_lines.append(line.strip())

    if current_title is not None:
        documents.append(
            GuidelineDocument(
                id=_slugify(current_title),
                title=current_title,
                source="Synthetic HEP demo guideline v0.1",
                summary=" ".join(summary_lines).strip(),
            )
        )

    return documents or _fallback_guidelines()


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "guideline"


def _fallback_guidelines() -> list[GuidelineDocument]:
    return [
        GuidelineDocument(
            id="hep-b-screening",
            title="Hepatitis B Screening",
            source="Synthetic HEP demo guideline v0.1",
            summary=(
                "Screen synthetic adult profiles with liver risk factors using HBsAg, "
                "anti-HBs, and anti-HBc. Confirm positives with follow-up testing."
            ),
        ),
        GuidelineDocument(
            id="hep-c-testing",
            title="Hepatitis C Testing",
            source="Synthetic HEP demo guideline v0.1",
            summary=(
                "Offer one-time HCV antibody screening in adult synthetic scenarios, "
                "then reflex to RNA confirmation before documenting active infection."
            ),
        ),
    ]


class GuidelineRetriever:
    def __init__(self, documents: list[GuidelineDocument] | None = None) -> None:
        self.documents = documents or load_guidelines_from_markdown()

    def search(self, query: str, limit: int = 3) -> GuidelineSearchOutput:
        query_terms = _tokenize(query)
        scored = sorted(
            (
                (_score(query_terms, _tokenize(f"{doc.title} {doc.summary}")), doc)
                for doc in self.documents
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        matches = [
            GuidelineChunk(
                id=doc.id,
                title=doc.title,
                source=doc.source,
                summary=doc.summary,
                score=round(score, 3),
            )
            for score, doc in scored[:limit]
            if score > 0
        ]
        if not matches:
            matches = [
                GuidelineChunk(
                    id=self.documents[0].id,
                    title=self.documents[0].title,
                    source=self.documents[0].source,
                    summary=self.documents[0].summary,
                    score=0.0,
                )
            ]
        return GuidelineSearchOutput(query=query, matches=matches)


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def _score(query_terms: set[str], document_terms: set[str]) -> float:
    if not query_terms or not document_terms:
        return 0.0
    overlap = len(query_terms & document_terms)
    return overlap / math.sqrt(len(query_terms) * len(document_terms))
