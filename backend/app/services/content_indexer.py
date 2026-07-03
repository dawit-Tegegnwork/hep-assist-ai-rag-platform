import re
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class ContentChunk:
    chunk_id: str
    title: str
    source: str
    content: str
    language: str


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "chunk"


def load_chunks_from_markdown(
    path: Path,
    *,
    language: str,
    source: str,
) -> list[ContentChunk]:
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    chunks: list[ContentChunk] = []
    current_title: str | None = None
    body_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                chunks.append(
                    ContentChunk(
                        chunk_id=f"{language}-{_slugify(current_title)}",
                        title=current_title,
                        source=source,
                        content=" ".join(body_lines).strip(),
                        language=language,
                    )
                )
            current_title = line[3:].strip()
            body_lines = []
            continue
        if current_title and line.strip() and not line.startswith("#"):
            body_lines.append(line.strip())

    if current_title is not None:
        chunks.append(
            ContentChunk(
                chunk_id=f"{language}-{_slugify(current_title)}",
                title=current_title,
                source=source,
                content=" ".join(body_lines).strip(),
                language=language,
            )
        )

    return chunks


def load_all_approved_chunks() -> list[ContentChunk]:
    en = load_chunks_from_markdown(
        DATA_DIR / "synthetic_guidelines.md",
        language="en",
        source="Synthetic HEP demo guideline v0.2",
    )
    am = load_chunks_from_markdown(
        DATA_DIR / "synthetic_guidelines_am.md",
        language="am",
        source="Synthetic HEP demo guideline v0.2 (Amharic examples)",
    )
    return en + am
