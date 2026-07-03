"""Tests for regulatory application workflow, RBAC, audit, and dashboard counts."""

from tests.conftest import auth_headers, client


def _submit_application(headers: dict[str, str] | None = None) -> dict:
    response = client.post(
        "/api/v1/regulatory/applications",
        headers=headers or auth_headers("applicant"),
        json={
            "product_name": "Test Product Alpha",
            "application_type": "marketing_authorization",
            "applicant_organization": "Synthetic Pharma Ltd",
            "dossier_summary": "Synthetic dossier for workflow testing with sufficient detail.",
            "supporting_documents": ["test_module.pdf"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_applicant_can_submit_application() -> None:
    body = _submit_application()
    assert body["status"] == "submitted"
    assert body["reference_number"].startswith("ERIS-DEMO-")


def test_reviewer_cannot_submit_application() -> None:
    response = client.post(
        "/api/v1/regulatory/applications",
        headers=auth_headers("reviewer"),
        json={
            "product_name": "Blocked Product",
            "application_type": "variation",
            "applicant_organization": "Demo Org",
            "dossier_summary": "Should be rejected by RBAC for reviewer role.",
        },
    )
    assert response.status_code == 403


def test_full_regulatory_workflow_with_audit() -> None:
    app_body = _submit_application()
    app_id = app_body["id"]

    start = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "start_technical_review", "comment": "Assigned for technical review"},
    )
    assert start.status_code == 200
    assert start.json()["status"] == "technical_review"

    clarify = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "request_clarification", "comment": "Need stability data appendix"},
    )
    assert clarify.status_code == 200
    assert clarify.json()["status"] == "clarification_requested"

    resubmit = client.post(
        f"/api/v1/regulatory/applications/{app_id}/resubmit",
        headers=auth_headers("applicant"),
        json={
            "dossier_summary": "Updated dossier with stability appendix attached for review.",
            "supporting_documents": ["test_module.pdf", "stability_appendix.pdf"],
            "applicant_note": "Addressed clarification request",
        },
    )
    assert resubmit.status_code == 200
    assert resubmit.json()["status"] == "resubmitted"

    restart = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "start_technical_review", "comment": "Re-opened after resubmission"},
    )
    assert restart.status_code == 200
    assert restart.json()["status"] == "technical_review"

    approve = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "approve", "comment": "Synthetic approval for demo"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    audit = client.get(
        f"/api/v1/regulatory/applications/{app_id}/audit",
        headers=auth_headers("auditor"),
    )
    assert audit.status_code == 200
    events = audit.json()
    actions = {e["action"] for e in events}
    assert "regulatory.application.submit" in actions
    assert "regulatory.application.transition" in actions
    transition_count = sum(1 for e in events if e["action"] == "regulatory.application.transition")
    assert transition_count >= 4


def test_invalid_transition_rejected() -> None:
    app_body = _submit_application()
    app_id = app_body["id"]

    invalid = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "approve", "comment": "Cannot approve before review"},
    )
    assert invalid.status_code == 400
    assert "Invalid transition" in invalid.json()["detail"]


def test_applicant_cannot_approve() -> None:
    app_body = _submit_application()
    app_id = app_body["id"]
    client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "start_technical_review"},
    )

    blocked = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("applicant"),
        json={"action": "approve"},
    )
    assert blocked.status_code == 403


def test_auditor_read_only() -> None:
    app_body = _submit_application()
    app_id = app_body["id"]

    blocked = client.post(
        f"/api/v1/regulatory/applications/{app_id}/transition",
        headers=auth_headers("auditor"),
        json={"action": "start_technical_review"},
    )
    assert blocked.status_code == 403

    listing = client.get("/api/v1/regulatory/applications", headers=auth_headers("auditor"))
    assert listing.status_code == 200


def test_regulatory_dashboard_counts() -> None:
    _submit_application()
    app2 = _submit_application()
    client.post(
        f"/api/v1/regulatory/applications/{app2['id']}/transition",
        headers=auth_headers("reviewer"),
        json={"action": "start_technical_review"},
    )

    summary = client.get(
        "/api/v1/regulatory/dashboard/summary",
        headers=auth_headers("reviewer"),
    )
    assert summary.status_code == 200
    data = summary.json()
    assert data["total"] >= 2
    assert data["submitted"] >= 1
    assert data["technical_review"] >= 1


def test_unauthenticated_access_denied() -> None:
    response = client.get("/api/v1/regulatory/applications")
    assert response.status_code == 401
