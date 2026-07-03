"""Synthetic sample payloads — no real patient data."""

from __future__ import annotations

from typing import Any

from app.interop.schemas import InteropSource

OPENMRS_VALID: dict[str, Any] = {
    "uuid": "patient-001-synthetic",
    "identifiers": [{"identifierType": "OpenMRS ID", "identifier": "SYN-OMRS-001"}],
    "person": {
        "givenName": "Abebe",
        "familyName": "Kebede",
        "birthdate": "1990-03-15",
        "gender": "M",
    },
    "encounters": [
        {
            "uuid": "encounter-001-synthetic",
            "encounterType": "Outpatient",
            "encounterDatetime": "2025-06-10T09:30:00",
            "obs": [
                {"concept": "5089AAAAAAAAAAAAAAAAAAAAAAAAAAAA", "value": "36.5", "obsDatetime": "2025-06-10T09:35:00"},
                {"concept": "5085AAAAAAAAAAAAAAAAAAAAAAAAAAAA", "value": "120/80", "obsDatetime": "2025-06-10T09:36:00"},
            ],
        }
    ],
}

OPENMRS_INVALID: dict[str, Any] = {
    "uuid": "patient-002-synthetic",
    "person": {"givenName": "Sara"},
    "encounters": [{"uuid": "enc-bad", "encounterDatetime": "not-a-date"}],
}

OPENELIS_VALID: dict[str, Any] = {
    "accessionNumber": "LAB-SYN-2025-0001",
    "patientId": "patient-001-synthetic",
    "collectionDate": "2025-06-11",
    "testResults": [
        {
            "testCode": "HGB",
            "testName": "Hemoglobin",
            "resultValue": "13.2",
            "resultUnit": "g/dL",
            "resultDateTime": "2025-06-11T14:00:00",
            "status": "final",
        },
        {
            "testCode": "WBC",
            "testName": "White Blood Cell Count",
            "resultValue": "6.1",
            "resultUnit": "10^3/uL",
            "resultDateTime": "2025-06-11T14:05:00",
            "status": "final",
        },
    ],
}

OPENELIS_INVALID: dict[str, Any] = {
    "accessionNumber": "LAB-SYN-2025-0002",
    "patientId": "patient-001-synthetic",
    "collectionDate": "2025-13-99",
    "testResults": [{"testCode": "HGB", "testName": "Hemoglobin"}],
}

DHIS2_VALID: dict[str, Any] = {
    "dataSet": "HIV_MONTHLY_SYNTHETIC",
    "orgUnit": "OU-ADDIS-DEMO",
    "period": "202506",
    "dataValues": [
        {"dataElement": "DE_NEW_HIV_POS", "value": 42, "categoryOptionCombo": "default"},
        {"dataElement": "DE_ART_STARTED", "value": 38},
    ],
}

DHIS2_INVALID: dict[str, Any] = {
    "dataSet": "HIV_MONTHLY_SYNTHETIC",
    "orgUnit": "OU-ADDIS-DEMO",
    "period": "June-2025",
    "dataValues": [],
}

FHIR_PATIENT_VALID: dict[str, Any] = {
    "resourceType": "Patient",
    "id": "fhir-patient-001-synthetic",
    "name": [{"family": "Tadesse", "given": ["Helen"]}],
    "gender": "female",
    "birthDate": "1988-07-22",
}

FHIR_OBSERVATION_VALID: dict[str, Any] = {
    "resourceType": "Observation",
    "id": "obs-001-synthetic",
    "status": "final",
    "code": {"text": "Hemoglobin"},
    "subject": {"reference": "Patient/fhir-patient-001-synthetic"},
    "effectiveDateTime": "2025-06-11T14:00:00",
    "valueQuantity": {"value": 13.2, "unit": "g/dL"},
}

FHIR_BUNDLE_VALID: dict[str, Any] = {
    "resourceType": "Bundle",
    "type": "collection",
    "id": "bundle-synthetic-001",
    "entry": [
        {"resource": FHIR_PATIENT_VALID},
        {"resource": FHIR_OBSERVATION_VALID},
    ],
}

FHIR_INVALID: dict[str, Any] = {
    "resourceType": "Observation",
    "id": "obs-bad-synthetic",
    "effectiveDateTime": "yesterday",
}

SAMPLES: dict[InteropSource, dict[str, dict[str, Any]]] = {
    InteropSource.OPENMRS: {"valid": OPENMRS_VALID, "invalid": OPENMRS_INVALID},
    InteropSource.OPENELIS: {"valid": OPENELIS_VALID, "invalid": OPENELIS_INVALID},
    InteropSource.DHIS2: {"valid": DHIS2_VALID, "invalid": DHIS2_INVALID},
    InteropSource.FHIR: {
        "valid": FHIR_BUNDLE_VALID,
        "invalid": FHIR_INVALID,
        "patient": FHIR_PATIENT_VALID,
        "observation": FHIR_OBSERVATION_VALID,
    },
}


def get_sample(source: InteropSource, variant: str = "valid") -> dict[str, Any]:
    bucket = SAMPLES[source]
    if variant not in bucket:
        raise KeyError(f"Unknown sample variant '{variant}' for {source.value}")
    return bucket[variant]
