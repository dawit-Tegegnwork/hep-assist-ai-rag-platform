from sqlmodel import Session

from app.db.session import get_engine
from app.services.content_indexer import load_all_approved_chunks
from app.services.embeddings import MockEmbeddingProvider, cosine_similarity, get_embedding_provider
from app.services.rag import GuidelineRetriever, VectorRetriever
from app.services.vector_store import VectorStore


def test_load_approved_chunks_includes_english_and_amharic() -> None:
    chunks = load_all_approved_chunks()
    languages = {chunk.language for chunk in chunks}
    assert "en" in languages
    assert "am" in languages
    assert len(chunks) >= 10


def test_mock_embedding_dimensions_and_determinism() -> None:
    provider = MockEmbeddingProvider(384)
    first = provider.embed("hepatitis screening")
    second = provider.embed("hepatitis screening")
    third = provider.embed("different query")

    assert len(first) == 384
    assert first == second
    assert first != third


def test_cosine_similarity_identical_vectors() -> None:
    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == 1.0


def test_vector_store_search_returns_relevant_chunk() -> None:
    with Session(get_engine()) as session:
        store = VectorStore(session)
        store.index_all(force=True)
        matches = store.search("hepatitis B screening HBsAg", limit=2, language="en")
        assert matches
        assert any("hepatitis" in match.title.lower() or "hepatitis" in match.summary.lower() for match in matches)


def test_vector_retriever_fallback_to_keyword() -> None:
    with Session(get_engine()) as session:
        retriever = VectorRetriever(session)
        result = retriever.search("HCV RNA testing", limit=2)
        assert result.matches
        assert result.matches[0].score >= 0


def test_keyword_retriever_still_works() -> None:
    result = GuidelineRetriever().search("liver safety jaundice", limit=1)
    assert result.matches[0].title


def test_get_embedding_provider_uses_mock_in_tests() -> None:
    provider = get_embedding_provider()
    assert provider.__class__.__name__ == "MockEmbeddingProvider"
