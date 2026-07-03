import hashlib
import math
import os
import re
from abc import ABC, abstractmethod

from app.core.config import get_settings

_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hash-based embeddings for tests and offline demos."""

    def __init__(self, dimensions: int = 384) -> None:
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> list[float]:
        return self._hash_embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_embed(text) for text in texts]

    def _hash_embed(self, text: str) -> list[float]:
        values = [0.0] * self._dimensions
        tokens = _TOKEN_PATTERN.findall(text.lower())
        if not tokens:
            tokens = [text.lower()[:32] or "empty"]

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for offset in range(0, min(len(digest), 16), 2):
                index = int.from_bytes(digest[offset : offset + 2], "big") % self._dimensions
                values[index] += 1.0

        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]


class FastEmbedProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise RuntimeError(
                "fastembed is not installed. Set MEDIMIND_EMBEDDING_PROVIDER=mock or pip install fastembed"
            ) from exc

        self._model = TextEmbedding(model_name)
        self._dimensions = 384

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> list[float]:
        return list(next(self._model.embed([text])))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [list(vec) for vec in self._model.embed(texts)]


_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    global _provider
    if _provider is not None:
        return _provider

    settings = get_settings()
    provider_name = os.getenv("MEDIMIND_EMBEDDING_PROVIDER", settings.embedding_provider)
    if provider_name == "mock":
        _provider = MockEmbeddingProvider(settings.embedding_dimensions)
    else:
        try:
            _provider = FastEmbedProvider(settings.embedding_model)
        except Exception:
            _provider = MockEmbeddingProvider(settings.embedding_dimensions)
    return _provider


def reset_embedding_provider() -> None:
    global _provider
    _provider = None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    denom = norm_a * norm_b
    if denom == 0.0:
        return 0.0
    return dot / denom
