"""Tests for healthcare interoperability modernization lab."""

import copy

import pytest
from fastapi.testclient import TestClient

from app.interop.schemas import InteropSource, MessageStatus, ValidationStatus
from app.interop.synthetic_data import get_sample
from app.main import app

client = TestClient(app)


@pytest.fixture
def openmrs_valid():
    return get_sample(InteropSource.OPENMRS, "valid")


@pytest.fixture
def openmrs_invalid():
    return get_sample(InteropSource.OPENMRS, "invalid")


def test_list_sources():
    response = client.get("/api/v1/interop/sources")
    assert response.status_code == 200
    data = response.json()
    assert "openmrs" in data["sources"]
    assert "openelis" in data["sources"]
    assert "dhis2" in data["sources"]
    assert "fhir" in data["sources"]


def test_get_sample_payloads():
    response = client.get("/api/v1/interop/samples/openelis")
    assert response.status_code == 200
    assert response.json()["accessionNumber"]


def test_ingest_valid_openmrs(openmrs_valid):
    payload = copy.deepcopy(openmrs_valid)
    payload["uuid"] = "test-openmrs-valid-001"
    payload["encounters"][0]["uuid"] = "test-enc-001"

    response = client.post("/api/v1/interop/ingest/openmrs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == ValidationStatus.PASSED.value
    assert data["status"] == MessageStatus.TRANSFORMED.value
    assert data["canonical_preview"]["source"] == "openmrs"
    assert len(data["canonical_preview"]["patients"]) == 1
    assert data["canonical_preview"]["patients"][0]["given_name"] == "Abebe"


def test_ingest_invalid_openmrs(openmrs_invalid):
    payload = copy.deepcopy(openmrs_invalid)
    payload["uuid"] = "test-openmrs-invalid-001"

    response = client.post("/api/v1/interop/ingest/openmrs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == ValidationStatus.FAILED.value
    assert data["status"] == MessageStatus.VALIDATION_FAILED.value
    assert len(data["validation_errors"]) > 0
    codes = {e["code"] for e in data["validation_errors"]}
    assert "invalid_date" in codes or "required_field" in codes


def test_transformation_openelis():
    payload = copy.deepcopy(get_sample(InteropSource.OPENELIS, "valid"))
    payload["accessionNumber"] = "TEST-LAB-001"

    response = client.post("/api/v1/interop/ingest/openelis", json=payload)
    assert response.status_code == 200
    data = response.json()
    canonical = data["canonical_preview"]
    assert len(canonical["lab_results"]) == 2
    assert canonical["lab_results"][0]["test_code"] == "HGB"


def test_transformation_dhis2():
    payload = copy.deepcopy(get_sample(InteropSource.DHIS2, "valid"))
    payload["period"] = "202507"

    response = client.post("/api/v1/interop/ingest/dhis2", json=payload)
    assert response.status_code == 200
    reports = response.json()["canonical_preview"]["aggregate_reports"]
    assert len(reports) == 2
    assert reports[0]["data_element"] == "DE_NEW_HIV_POS"


def test_transformation_fhir_bundle():
    payload = copy.deepcopy(get_sample(InteropSource.FHIR, "valid"))
    payload["id"] = "bundle-test-001"
    payload["entry"][0]["resource"]["id"] = "fhir-patient-test-001"

    response = client.post("/api/v1/interop/ingest/fhir", json=payload)
    assert response.status_code == 200
    canonical = response.json()["canonical_preview"]
    assert len(canonical["fhir_resources"]) == 2
    assert len(canonical["patients"]) == 1


def test_duplicate_detection(openmrs_valid):
    payload = copy.deepcopy(openmrs_valid)
    payload["uuid"] = "test-duplicate-001"
    payload["encounters"][0]["uuid"] = "test-enc-dup-001"

    first = client.post("/api/v1/interop/ingest/openmrs", json=payload)
    assert first.status_code == 200

    second = client.post("/api/v1/interop/ingest/openmrs", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "duplicate_id"


def test_audit_log_on_ingest(openmrs_valid):
    payload = copy.deepcopy(openmrs_valid)
    payload["uuid"] = "test-audit-001"
    payload["encounters"][0]["uuid"] = "test-enc-audit-001"

    client.post("/api/v1/interop/ingest/openmrs", json=payload)

    audit = client.get("/api/v1/interop/audit?limit=20")
    assert audit.status_code == 200
    events = audit.json()
    actions = [e["action"] for e in events]
    assert "payload_received" in actions
    assert "validation_passed" in actions
    assert "transformed" in actions


def test_export_after_valid_ingest(openmrs_valid):
    payload = copy.deepcopy(openmrs_valid)
    payload["uuid"] = "test-export-001"
    payload["encounters"][0]["uuid"] = "test-enc-export-001"

    ingest = client.post("/api/v1/interop/ingest/openmrs", json=payload)
    message_id = ingest.json()["message_id"]

    export = client.post(f"/api/v1/interop/messages/{message_id}/export")
    assert export.status_code == 200
    body = export.json()
    assert body["payload"]["synthetic_only"] is True
    assert "canonical" in body["payload"]

    audit = client.get("/api/v1/interop/audit?limit=5")
    assert any(e["action"] == "exported" for e in audit.json())


def test_dashboard_stats(openmrs_valid):
    payload = copy.deepcopy(openmrs_valid)
    payload["uuid"] = "test-dashboard-001"
    payload["encounters"][0]["uuid"] = "test-enc-dash-001"
    client.post("/api/v1/interop/ingest/openmrs", json=payload)

    stats = client.get("/api/v1/interop/dashboard/stats")
    assert stats.status_code == 200
    data = stats.json()
    assert data["total_messages"] >= 1
    assert "latest_events" in data
    assert isinstance(data["latest_events"], list)


def test_invalid_lab_missing_fields():
    payload = copy.deepcopy(get_sample(InteropSource.OPENELIS, "invalid"))
    payload["accessionNumber"] = "TEST-LAB-INVALID-001"

    response = client.post("/api/v1/interop/ingest/openelis", json=payload)
    assert response.status_code == 200
    errors = response.json()["validation_errors"]
    assert any(e["code"] in ("missing_lab_field", "invalid_date") for e in errors)


def test_interop_dashboard_page():
    response = client.get("/interop/dashboard")
    assert response.status_code == 200
    assert "Interoperability Modernization Lab" in response.text
