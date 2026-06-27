from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "MediMind HEP Assist AI"
    api_prefix: str = "/api/v1"
    audit_log_path: Path = Path("audit_logs.jsonl")
    database_url: str | None = Field(
        default=None,
        description="Optional PostgreSQL URL for durable audit logging.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEDIMIND_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

