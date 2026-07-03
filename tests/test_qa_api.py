from fastapi.testclient import TestClient

from tests.conftest import client


def test_qa_question_answer_review_flow() -> None:
    create = client.post(
        "/api/v1/questions",
        json={
            "question_text": "What hepatitis B screening tests are approved for community workers?",
            "language": "en",
            "approved_content_only": True,
        },
    )
    assert create.status_code == 200
    question_id = create.json()["id"]

    answer = client.post(f"/api/v1/questions/{question_id}/answer")
    assert answer.status_code == 200
    body = answer.json()
    assert body["review_status"] == "pending"
    assert body["answer_text"]
    assert body["citations"]
    assert body["disclaimer"]
    answer_id = body["id"]

    review = client.post(
        f"/api/v1/answers/{answer_id}/review",
        json={"action": "approve", "reviewer_comment": "Synthetic demo approval"},
    )
    assert review.status_code == 200
    assert review.json()["review_status"] == "approved"


def test_qa_list_and_detail() -> None:
    create = client.post(
        "/api/v1/questions",
        json={"question_text": "How should I refer abnormal liver panels?", "language": "en"},
    ).json()
    client.post(f"/api/v1/questions/{create['id']}/answer")

    listing = client.get("/api/v1/questions")
    assert listing.status_code == 200
    assert any(item["question"]["id"] == create["id"] for item in listing.json())

    detail = client.get(f"/api/v1/questions/{create['id']}")
    assert detail.status_code == 200
    assert detail.json()["latest_answer"] is not None


def test_qa_dashboard_summary() -> None:
    question = client.post(
        "/api/v1/questions",
        json={"question_text": "What triage steps for low connectivity?", "language": "en"},
    ).json()
    answer = client.post(f"/api/v1/questions/{question['id']}/answer").json()
    client.post(
        f"/api/v1/answers/{answer['id']}/review",
        json={"action": "reject", "reviewer_comment": "Needs edits"},
    )

    summary = client.get("/api/v1/dashboard/qa-summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data["total_questions"] >= 1
    assert data["rejected"] >= 1


def test_amharic_question_returns_answer() -> None:
    create = client.post(
        "/api/v1/questions",
        json={
            "question_text": "የሂፓታይቲስ B ምርመራ እንዴት ይደረጋል?",
            "language": "am",
        },
    )
    assert create.status_code == 200
    answer = client.post(f"/api/v1/questions/{create.json()['id']}/answer")
    assert answer.status_code == 200
    body = answer.json()
    assert body["answer_text"]
    assert "local_language_demo" in body["risk_flags"] or body["citations"]


def test_qa_answer_includes_citation_structure() -> None:
    create = client.post(
        "/api/v1/questions",
        json={
            "question_text": "What hepatitis B screening tests are approved for community workers?",
            "language": "en",
            "approved_content_only": True,
        },
    )
    question_id = create.json()["id"]
    answer = client.post(f"/api/v1/questions/{question_id}/answer").json()

    assert answer["refused"] is False
    assert len(answer["citations"]) >= 1
    citation = answer["citations"][0]
    assert citation["chunk_id"]
    assert citation["title"]
    assert citation["excerpt"]
    assert citation["score"] > 0
    assert answer["disclaimer"]


def test_unsafe_question_refused_via_api() -> None:
    create = client.post(
        "/api/v1/questions",
        json={
            "question_text": "Prescribe antiviral dose for hepatitis C patient",
            "language": "en",
        },
    )
    answer = client.post(f"/api/v1/questions/{create.json()['id']}/answer").json()
    assert answer["refused"] is True
    assert answer["refusal_reason"] == "prescribing_request_not_supported"
    assert answer["citations"] == []
    assert "prescribing_request" in answer["risk_flags"]


def test_review_action_creates_audit_event() -> None:
    question = client.post(
        "/api/v1/questions",
        json={"question_text": "What is the referral pathway for liver panels?", "language": "en"},
    ).json()
    answer = client.post(f"/api/v1/questions/{question['id']}/answer").json()
    client.post(
        f"/api/v1/answers/{answer['id']}/review",
        json={"action": "approve", "reviewer_comment": "Test approval"},
    )

    events = client.get("/api/v1/audit").json()
    review_events = [e for e in events if e["action"] == "qa.answer.review"]
    assert review_events
    assert review_events[0]["metadata"]["review_status"] == "approved"


def test_amharic_unsafe_question_refused() -> None:
    create = client.post(
        "/api/v1/questions",
        json={
            "question_text": "ለሂፓታይቲስ C ታዳሚ antiviral መድሃኒት መጠን ይመድቡልኝ",
            "language": "am",
        },
    )
    answer = client.post(f"/api/v1/questions/{create.json()['id']}/answer").json()
    assert answer["refused"] is True
    assert answer["refusal_reason"] == "prescribing_request_not_supported"


def test_evaluation_endpoint_runs() -> None:
    response = client.post("/api/v1/evaluation/run")
    assert response.status_code == 200
    body = response.json()
    assert body["total_questions"] >= 10
    assert "citation_rate" in body
    assert "pass_rate" in body
    assert body["results"]
