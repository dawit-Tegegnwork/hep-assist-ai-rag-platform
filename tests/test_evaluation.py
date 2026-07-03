"""Tests for golden evaluation pass/fail scoring."""

from fastapi.testclient import TestClient

from tests.conftest import client


def test_evaluation_pass_fail_fields() -> None:
    response = client.post("/api/v1/evaluation/run")
    assert response.status_code == 200
    body = response.json()
    assert "pass_rate" in body
    assert "passed" in body
    assert body["total_questions"] >= 10
    assert all("passed" in row for row in body["results"])
    assert body["pass_rate"] >= 0.7


def test_evaluation_refusal_cases_pass() -> None:
    body = client.post("/api/v1/evaluation/run").json()
    refusal_rows = [r for r in body["results"] if r["expected_topic"] == "refusal"]
    assert len(refusal_rows) >= 2
    assert all(r["refused"] and r["passed"] for r in refusal_rows)
