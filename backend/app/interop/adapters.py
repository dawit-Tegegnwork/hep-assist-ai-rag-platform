"""Adapters translate source-specific payloads into canonical internal models."""

from __future__ import annotations

from typing import Any

from app.interop.schemas import (
    CanonicalAggregateReport,
    CanonicalBundle,
    CanonicalEncounter,
    CanonicalLabResult,
    CanonicalPatient,
    InteropSource,
)


def _openmrs_patient(payload: dict[str, Any]) -> CanonicalPatient:
    person = payload.get("person") or {}
    return CanonicalPatient(
        external_id=str(payload["uuid"]),
        source_system="openmrs-sim",
        given_name=str(person.get("givenName", "")),
        family_name=str(person.get("familyName", "")),
        birth_date=person.get("birthdate"),
        gender=person.get("gender"),
        identifiers=[{"type": i.get("identifierType", "unknown"), "value": i.get("identifier", "")} for i in payload.get("identifiers", [])],
    )


def adapt_openmrs(payload: dict[str, Any], message_id: str) -> CanonicalBundle:
    patient = _openmrs_patient(payload)
    encounters = []
    for enc in payload.get("encounters") or []:
        encounters.append(
            CanonicalEncounter(
                external_id=str(enc.get("uuid", "")),
                patient_external_id=patient.external_id,
                encounter_type=enc.get("encounterType"),
                encounter_datetime=enc.get("encounterDatetime"),
                observations=[
                    {
                        "concept": obs.get("concept"),
                        "value": obs.get("value"),
                        "obsDatetime": obs.get("obsDatetime"),
                    }
                    for obs in enc.get("obs") or []
                ],
            )
        )
    return CanonicalBundle(message_id=message_id, source=InteropSource.OPENMRS, patients=[patient], encounters=encounters)


def adapt_openelis(payload: dict[str, Any], message_id: str) -> CanonicalBundle:
    patient_id = str(payload["patientId"])
    lab_results = [
        CanonicalLabResult(
            accession_number=str(payload["accessionNumber"]),
            patient_external_id=patient_id,
            test_code=str(test.get("testCode", "")),
            test_name=str(test.get("testName", "")),
            result_value=str(test.get("resultValue", "")),
            result_unit=test.get("resultUnit"),
            result_datetime=test.get("resultDateTime"),
            status=str(test.get("status", "final")),
        )
        for test in payload.get("testResults") or []
    ]
    return CanonicalBundle(
        message_id=message_id,
        source=InteropSource.OPENELIS,
        patients=[
            CanonicalPatient(
                external_id=patient_id,
                source_system="openelis-sim",
                given_name="",
                family_name="",
            )
        ],
        lab_results=lab_results,
    )


def adapt_dhis2(payload: dict[str, Any], message_id: str) -> CanonicalBundle:
    reports = [
        CanonicalAggregateReport(
            data_element=str(dv.get("dataElement", "")),
            org_unit=str(payload.get("orgUnit", "")),
            period=str(payload.get("period", "")),
            value=float(dv.get("value", 0)),
            category_option_combo=dv.get("categoryOptionCombo"),
        )
        for dv in payload.get("dataValues") or []
    ]
    return CanonicalBundle(message_id=message_id, source=InteropSource.DHIS2, aggregate_reports=reports)


def adapt_fhir(payload: dict[str, Any], message_id: str) -> CanonicalBundle:
    resources: list[dict[str, Any]] = []
    patients: list[CanonicalPatient] = []
    lab_results: list[CanonicalLabResult] = []

    def handle_resource(resource: dict[str, Any]) -> None:
        resources.append(resource)
        rtype = resource.get("resourceType")
        if rtype == "Patient":
            name = (resource.get("name") or [{}])[0]
            patients.append(
                CanonicalPatient(
                    external_id=str(resource.get("id", "")),
                    source_system="fhir-sim",
                    given_name=" ".join(name.get("given") or []),
                    family_name=str(name.get("family", "")),
                    birth_date=resource.get("birthDate"),
                    gender=resource.get("gender"),
                )
            )
        elif rtype == "Observation":
            value = resource.get("valueQuantity") or {}
            lab_results.append(
                CanonicalLabResult(
                    accession_number=str(resource.get("id", "")),
                    patient_external_id=str((resource.get("subject") or {}).get("reference", "").split("/")[-1]),
                    test_code=str((resource.get("code") or {}).get("text", "observation")),
                    test_name=str((resource.get("code") or {}).get("text", "Observation")),
                    result_value=str(value.get("value", resource.get("valueString", ""))),
                    result_unit=value.get("unit"),
                    result_datetime=resource.get("effectiveDateTime"),
                    status=str(resource.get("status", "final")),
                )
            )

    if payload.get("resourceType") == "Bundle":
        for entry in payload.get("entry") or []:
            if entry.get("resource"):
                handle_resource(entry["resource"])
    else:
        handle_resource(payload)

    return CanonicalBundle(
        message_id=message_id,
        source=InteropSource.FHIR,
        patients=patients,
        lab_results=lab_results,
        fhir_resources=resources,
    )


def adapt_payload(source: InteropSource, payload: dict[str, Any], message_id: str) -> CanonicalBundle:
    adapters = {
        InteropSource.OPENMRS: adapt_openmrs,
        InteropSource.OPENELIS: adapt_openelis,
        InteropSource.DHIS2: adapt_dhis2,
        InteropSource.FHIR: adapt_fhir,
    }
    return adapters[source](payload, message_id)
