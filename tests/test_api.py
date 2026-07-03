from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Community Health AI Modernization Lab"


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


def test_create_note_and_extract_workflow() -> None:
    create = client.post(
        "/api/v1/notes",
        json={
            "title": "Synthetic workflow note",
            "raw_text": "Synthetic patient with fatigue and hepatitis screening history.",
            "note_type": "clinical",
        },
    )
    assert create.status_code == 200
    note_id = create.json()["id"]

    extract = client.post(f"/api/v1/notes/{note_id}/extract")
    assert extract.status_code == 200
    body = extract.json()
    assert body["review_status"] == "pending"
    assert body["summary"]
    extraction_id = body["id"]

    review = client.post(
        f"/api/v1/extractions/{extraction_id}/review",
        json={"action": "approve", "reviewer_comment": "Synthetic demo approval"},
    )
    assert review.status_code == 200
    assert review.json()["review_status"] == "approved"


def test_dashboard_summary_reflects_review_states() -> None:
    note = client.post(
        "/api/v1/notes",
        json={"title": "Dash note", "raw_text": "Synthetic hepatitis follow-up note.", "note_type": "clinical"},
    ).json()
    extraction = client.post(f"/api/v1/notes/{note['id']}/extract").json()
    client.post(
        f"/api/v1/extractions/{extraction['id']}/review",
        json={"action": "reject", "reviewer_comment": "Needs edits"},
    )

    summary = client.get("/api/v1/dashboard/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data["total_notes"] >= 1
    assert data["rejected"] >= 1


def test_audit_events_are_listed() -> None:
    client.post(
        "/api/v1/notes",
        json={"title": "Audit note", "raw_text": "Synthetic audit trail demo.", "note_type": "clinical"},
    )
    response = client.get("/api/v1/audit")
    assert response.status_code == 200
    events = response.json()
    assert any(e["action"] == "note.create" for e in events)


def test_get_note_returns_latest_extraction() -> None:
    note_id = client.post(
        "/api/v1/notes",
        json={"title": "Detail note", "raw_text": "Synthetic detail check.", "note_type": "clinical"},
    ).json()["id"]
    client.post(f"/api/v1/notes/{note_id}/extract")

    detail = client.get(f"/api/v1/notes/{note_id}")
    assert detail.status_code == 200
    assert detail.json()["latest_extraction"] is not None


def test_dashboard_page_loads() -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Healthcare AI Workflow Assistant" in response.text
