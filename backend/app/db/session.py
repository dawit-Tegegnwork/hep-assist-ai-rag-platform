from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = settings.database_url or "sqlite:///./healthcare_ai.db"
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, echo=False, connect_args=connect_args)
    return _engine


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


def reset_engine(url: str | None = None) -> None:
    global _engine
    if url is not None:
        settings.database_url = url
    _engine = None
