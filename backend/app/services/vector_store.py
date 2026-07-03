from sqlmodel import Session, select

from app.db.models import ApprovedContentChunk
from app.models.schemas import GuidelineChunk
from app.services.content_indexer import ContentChunk, load_all_approved_chunks
from app.services.embeddings import cosine_similarity, get_embedding_provider


class VectorStore:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.embedder = get_embedding_provider()

    def index_all(self, force: bool = False) -> int:
        existing = self.session.exec(select(ApprovedContentChunk)).first()
        if existing and not force:
            return 0

        if force:
            for chunk in self.session.exec(select(ApprovedContentChunk)).all():
                self.session.delete(chunk)
            self.session.commit()

        chunks = load_all_approved_chunks()
        texts = [f"{c.title}. {c.content}" for c in chunks]
        embeddings = self.embedder.embed_batch(texts)

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            record = ApprovedContentChunk(
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                source=chunk.source,
                content=chunk.content,
                language=chunk.language,
                embedding=embedding,
            )
            self.session.add(record)
        self.session.commit()
        return len(chunks)

    def search(
        self,
        query: str,
        *,
        limit: int = 3,
        language: str | None = None,
        min_score: float = 0.0,
    ) -> list[GuidelineChunk]:
        query_embedding = self.embedder.embed(query)
        statement = select(ApprovedContentChunk)
        if language:
            statement = statement.where(ApprovedContentChunk.language == language)
        records = list(self.session.exec(statement).all())

        if not records:
            return []

        scored: list[tuple[float, ApprovedContentChunk]] = []
        for record in records:
            if not record.embedding:
                continue
            score = cosine_similarity(query_embedding, record.embedding)
            if score >= min_score:
                scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)
        if not scored and records:
            record = records[0]
            return [
                GuidelineChunk(
                    id=record.chunk_id,
                    title=record.title,
                    source=record.source,
                    summary=record.content,
                    score=0.0,
                    language=record.language,
                )
            ]

        return [
            GuidelineChunk(
                id=record.chunk_id,
                title=record.title,
                source=record.source,
                summary=record.content,
                score=round(score, 3),
                language=record.language,
            )
            for score, record in scored[:limit]
        ]
