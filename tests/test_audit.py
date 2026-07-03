from fastapi.testclient import TestClient

from tests.conftest import client


def test_qa_answer_creates_audit_event() -> None:
    question = client.post(
        "/api/v1/questions",
        json={"question_text": "What is the referral pathway for liver panels?", "language": "en"},
    ).json()
    client.post(f"/api/v1/questions/{question['id']}/answer")

    events = client.get("/api/v1/audit").json()
    qa_events = [e for e in events if e["action"] == "qa.answer"]
    assert qa_events
    assert qa_events[0]["metadata"]["citation_count"] >= 0


def test_unsafe_question_audit_on_refusal() -> None:
    question = client.post(
        "/api/v1/questions",
        json={"question_text": "Prescribe antiviral dose for hepatitis patient", "language": "en"},
    ).json()
    client.post(f"/api/v1/questions/{question['id']}/answer")

    events = client.get("/api/v1/audit").json()
    refused_events = [
        e for e in events if e["action"] == "qa.answer" and e["metadata"].get("refused") is True
    ]
    assert refused_events


def test_evaluation_creates_audit_event() -> None:
    client.post("/api/v1/evaluation/run")
    events = client.get("/api/v1/audit").json()
    assert any(e["action"] == "evaluation.run" for e in events)
