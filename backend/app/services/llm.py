import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.services.preprocessing import preprocess_clinical_text


class LLMProvider(ABC):
    @abstractmethod
    def extract(self, note_text: str, note_type: str = "clinical") -> dict[str, Any]:
        pass


class MockLLMProvider(LLMProvider):
    """Deterministic synthetic extraction for portfolio demos."""

    def extract(self, note_text: str, note_type: str = "clinical") -> dict[str, Any]:
        cleaned = preprocess_clinical_text(note_text)
        text = cleaned.normalized.lower()
        risk_flags: list[str] = []
        follow_up: list[str] = ["Schedule clinician review of AI output"]

        if any(term in text for term in ("hepatitis", "hcv", "hbv", "liver")):
            risk_flags.append("hepatitis_related_findings")
            follow_up.append("Confirm synthetic hepatitis screening pathway")
        if any(term in text for term in ("fatigue", "jaundice", "nausea")):
            risk_flags.append("symptom_follow_up_needed")
        if cleaned.redactions:
            risk_flags.append("identifiers_redacted_in_source")

        summary = (
            f"Synthetic {note_type} note summary: "
            f"{cleaned.normalized[:240]}{'...' if len(cleaned.normalized) > 240 else ''}"
        )
        return {
            "summary": summary,
            "follow_up_tasks": follow_up,
            "risk_flags": risk_flags,
            "structured_payload": {
                "note_type": note_type,
                "token_count": cleaned.token_count,
                "redaction_count": len(cleaned.redactions),
                "keywords": _keyword_hits(text),
            },
        }


class OpenAICompatibleProvider(LLMProvider):
    """Optional provider enabled via OPENAI_BASE_URL and OPENAI_API_KEY."""

    def __init__(self) -> None:
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def extract(self, note_text: str, note_type: str = "clinical") -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI-compatible provider")

        prompt = (
            "Extract structured JSON from this synthetic clinical note. "
            "Return keys: summary, follow_up_tasks (array), risk_flags (array), "
            "structured_payload (object). Do not diagnose. Note type: "
            f"{note_type}. Note:\n{note_text}"
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def get_llm_provider() -> LLMProvider:
    if os.getenv("OPENAI_API_KEY"):
        return OpenAICompatibleProvider()
    return MockLLMProvider()


def _keyword_hits(text: str) -> list[str]:
    keywords = ["hepatitis", "fatigue", "lab", "screening", "follow-up", "medication"]
    return [kw for kw in keywords if kw in text]
