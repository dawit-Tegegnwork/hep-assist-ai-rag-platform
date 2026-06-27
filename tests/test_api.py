from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def setup_module() -> None:
    settings.audit_log_path = Path("test_audit_logs.jsonl")
    if settings.audit_log_path.exists():
        settings.audit_log_path.unlink()


def teardown_module() -> None:
    if settings.audit_log_path.exists():
        settings.audit_log_path.unlink()


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_preprocess_redacts_identifiers_and_expands_abbreviations() -> None:
    response = client.post(
        "/api/v1/clinical/preprocess",
        json={"text": "Pt hx of SOB. Call +1 555 222 3333 on 2026-01-02."},
    )

    assert response.status_code == 200
    body = response.json()
    assert "[REDACTED_PHONE]" in body["cleaned"]
    assert "[REDACTED_DATE]" in body["cleaned"]
    assert "history of shortness of breath" in body["normalized"]


def test_guideline_search_returns_synthetic_matches() -> None:
    response = client.post(
        "/api/v1/guidelines/search",
        json={"query": "HCV RNA testing", "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["matches"]
    assert body["matches"][0]["id"] == "hepatitis-c-testing"
    assert "Synthetic" in body["disclaimer"]


def test_preprocess_leaves_clean_text_unchanged_when_no_patterns() -> None:
    response = client.post(
        "/api/v1/clinical/preprocess",
        json={"text": "Synthetic patient reports mild fatigue."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["redactions"] == []
    assert "fatigue" in body["normalized"]


def test_guideline_search_returns_fallback_for_unmatched_query() -> None:
    response = client.post(
        "/api/v1/guidelines/search",
        json={"query": "xyz unmatched terms", "limit": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["matches"]
    assert body["matches"][0]["title"]


def test_soap_note_minimal_input() -> None:
    response = client.post(
        "/api/v1/soap-note",
        json={"chief_complaint": "Fatigue", "history": "Synthetic demo.", "problems": []},
    )

    assert response.status_code == 200
    body = response.json()
    assert "Fatigue" in body["subjective"]
    assert "not medical advice" in body["disclaimer"]


def test_soap_note_uses_synthetic_guideline_plan() -> None:
    response = client.post(
        "/api/v1/soap-note",
        json={
            "chief_complaint": "Fatigue",
            "history": "Synthetic patient reports hx of hepatitis exposure.",
            "vitals": {"temp_c": 37.2, "hr": 82},
            "problems": ["hepatitis screening"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "Fatigue" in body["subjective"]
    assert body["plan"]
    assert "not medical advice" in body["disclaimer"]

