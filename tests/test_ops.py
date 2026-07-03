from fastapi.testclient import TestClient

from tests.conftest import client


def test_liveness_endpoint() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint() -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "connected"


def test_health_includes_checks() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert body["service"] == "Community Health AI Modernization Lab"
    assert "checks" in body
    assert body["checks"]["database"]["ok"] is True


def test_request_id_header_present() -> None:
    response = client.get("/health/live")
    assert response.headers.get("X-Request-ID")
