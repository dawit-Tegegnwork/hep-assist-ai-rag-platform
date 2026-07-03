from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "HEP Assist AI RAG Platform"
    api_prefix: str = "/api/v1"
    audit_log_path: Path = Path("audit_logs.jsonl")
    database_url: str | None = Field(
        default="sqlite:///./healthcare_ai.db",
        description="PostgreSQL or SQLite URL for notes, extractions, and audit events.",
    )
    llm_provider: str = Field(default="mock", description="mock or openai")
    embedding_provider: str = Field(default="fastembed", description="fastembed or mock")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")
    embedding_dimensions: int = Field(default=384)
    retrieval_top_k: int = Field(default=3, ge=1, le=10)
    retrieval_min_score: float = Field(default=0.35, ge=0.0, le=1.0)
    approved_content_only_default: bool = Field(default=True)
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173"])

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEDIMIND_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
