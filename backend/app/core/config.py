from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "Community Health AI Modernization Lab"
    app_version: str = "1.1.0"
    environment: str = Field(default="development", description="development, staging, or production")
    api_prefix: str = "/api/v1"
    audit_log_path: Path = Path("audit_logs.jsonl")
    database_url: str | None = Field(
        default="sqlite:///./healthcare_ai.db",
        description="PostgreSQL or SQLite URL for notes, extractions, and audit events.",
    )
    llm_provider: str = Field(default="mock", description="mock or openai")
    embedding_provider: str = Field(default="mock", description="mock or fastembed")
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")
    embedding_dimensions: int = Field(default=384)
    retrieval_top_k: int = Field(default=3, ge=1, le=10)
    retrieval_min_score: float = Field(default=0.35, ge=0.0, le=1.0)
    approved_content_only_default: bool = Field(default=True)
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]
    )
    log_level: str = Field(default="INFO")
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_per_minute: int = Field(default=120, ge=10, le=1000)
    auto_seed_on_startup: bool = Field(default=True)
    frontend_url: str = Field(default="http://localhost:5173")
    auth_enabled: bool = Field(default=True)
    auth_secret_key: str = Field(default="synthetic-health-modernization-demo-secret-change-in-production")
    auth_algorithm: str = Field(default="HS256")
    auth_token_expire_hours: int = Field(default=8, ge=1, le=72)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEDIMIND_")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value  # type: ignore[return-value]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if os.getenv("OPENAI_API_KEY"):
        settings.llm_provider = "openai"
    return settings


settings = get_settings()
