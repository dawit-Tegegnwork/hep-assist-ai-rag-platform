import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import init_db, reset_engine
from app.main import app
from app.services.embeddings import reset_embedding_provider

client = TestClient(app)


@pytest.fixture(autouse=True)
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    reset_engine(f"sqlite:///{db_path}")
    reset_embedding_provider()
    monkeypatch.setenv("MEDIMIND_EMBEDDING_PROVIDER", "mock")
    settings.embedding_provider = "mock"
    settings.rate_limit_enabled = False
    settings.auto_seed_on_startup = False
    settings.audit_log_path = tmp_path / "audit_logs.jsonl"
    init_db()
    from app.services.vector_store import VectorStore
    from app.db.session import get_engine
    from sqlmodel import Session

    with Session(get_engine()) as session:
        VectorStore(session).index_all(force=True)
    yield
    reset_engine(f"sqlite:///{db_path}")
    reset_embedding_provider()
