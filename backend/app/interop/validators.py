"""Validation layer for interoperability payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.interop.schemas import InteropSource, ValidationErrorDetail


def _parse_date(value: str | None) -> bool:
    if not value:
        return False
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            datetime.strptime(value.replace("+00:00", "Z").rstrip("Z") + ("Z" if "T" in value and not value.endswith("Z") else ""), fmt if "T" not in fmt else fmt)
            return True
        except ValueError:
            continue
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _require(errors: list[ValidationErrorDetail], payload: dict, field: str, code: str = "required_field") -> Any | None:
    parts = field.split(".")
    current: Any = payload
    for part in parts:
        if not isinstance(current, dict) or part not in current or current[part] in (None, ""):
            errors.append(ValidationErrorDetail(field=field, code=code, message=f"Missing required field: {field}"))
            return None
        current = current[part]
    return current


def validate_openmrs(payload: dict[str, Any]) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    _require(errors, payload, "uuid")
    _require(errors, payload, "person.givenName")
    _require(errors, payload, "person.familyName")
    birth = _require(errors, payload, "person.birthdate")
    if birth and not _parse_date(str(birth)):
        errors.append(ValidationErrorDetail(field="person.birthdate", code="invalid_date", message="Invalid birthdate format"))
    encounters = payload.get("encounters") or []
    if not encounters:
        errors.append(ValidationErrorDetail(field="encounters", code="required_field", message="At least one encounter is required"))
    for idx, enc in enumerate(encounters):
        if not enc.get("uuid"):
            errors.append(ValidationErrorDetail(field=f"encounters[{idx}].uuid", code="required_field", message="Encounter uuid required"))
        enc_dt = enc.get("encounterDatetime")
        if enc_dt and not _parse_date(str(enc_dt)):
            errors.append(ValidationErrorDetail(field=f"encounters[{idx}].encounterDatetime", code="invalid_date", message="Invalid encounter datetime"))
    return errors


def validate_openelis(payload: dict[str, Any]) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    _require(errors, payload, "accessionNumber")
    _require(errors, payload, "patientId")
    _require(errors, payload, "collectionDate")
    collection = payload.get("collectionDate")
    if collection and not _parse_date(str(collection)):
        errors.append(ValidationErrorDetail(field="collectionDate", code="invalid_date", message="Invalid collection date"))
    tests = payload.get("testResults") or []
    if not tests:
        errors.append(ValidationErrorDetail(field="testResults", code="required_field", message="At least one test result is required"))
    for idx, test in enumerate(tests):
        for field in ("testCode", "testName", "resultValue"):
            if not test.get(field):
                errors.append(
                    ValidationErrorDetail(
                        field=f"testResults[{idx}].{field}",
                        code="missing_lab_field",
                        message=f"Lab result missing required field: {field}",
                    )
                )
        result_dt = test.get("resultDateTime")
        if result_dt and not _parse_date(str(result_dt)):
            errors.append(ValidationErrorDetail(field=f"testResults[{idx}].resultDateTime", code="invalid_date", message="Invalid result datetime"))
    return errors


def validate_dhis2(payload: dict[str, Any]) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    _require(errors, payload, "dataSet")
    _require(errors, payload, "orgUnit")
    _require(errors, payload, "period")
    period = payload.get("period")
    if period and not str(period).isdigit():
        errors.append(ValidationErrorDetail(field="period", code="invalid_period", message="DHIS2 period must be YYYYMM or YYYYMMdd numeric format"))
    data_values = payload.get("dataValues") or []
    if not data_values:
        errors.append(ValidationErrorDetail(field="dataValues", code="required_field", message="At least one data value is required"))
    for idx, dv in enumerate(data_values):
        if not dv.get("dataElement"):
            errors.append(ValidationErrorDetail(field=f"dataValues[{idx}].dataElement", code="required_field", message="dataElement required"))
        if dv.get("value") is None:
            errors.append(ValidationErrorDetail(field=f"dataValues[{idx}].value", code="required_field", message="value required"))
    return errors


def validate_fhir(payload: dict[str, Any]) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    resource_type = payload.get("resourceType")
    if not resource_type:
        errors.append(ValidationErrorDetail(field="resourceType", code="required_field", message="FHIR resourceType required"))
        return errors
    if resource_type == "Patient":
        if not payload.get("id"):
            errors.append(ValidationErrorDetail(field="id", code="required_field", message="Patient id required"))
        names = payload.get("name") or []
        if not names or not names[0].get("family"):
            errors.append(ValidationErrorDetail(field="name[0].family", code="required_field", message="Patient family name required"))
        birth = None
        for ident in ["birthDate"]:
            birth = payload.get(ident)
        if birth and not _parse_date(str(birth)):
            errors.append(ValidationErrorDetail(field="birthDate", code="invalid_date", message="Invalid birthDate"))
    elif resource_type == "Observation":
        if not payload.get("id"):
            errors.append(ValidationErrorDetail(field="id", code="required_field", message="Observation id required"))
        if not payload.get("status"):
            errors.append(ValidationErrorDetail(field="status", code="required_field", message="Observation status required"))
        if payload.get("valueQuantity") is None and payload.get("valueString") is None:
            errors.append(ValidationErrorDetail(field="value", code="missing_lab_field", message="Observation value required"))
        effective = payload.get("effectiveDateTime")
        if effective and not _parse_date(str(effective)):
            errors.append(ValidationErrorDetail(field="effectiveDateTime", code="invalid_date", message="Invalid effectiveDateTime"))
    elif resource_type == "Bundle":
        entries = payload.get("entry") or []
        if not entries:
            errors.append(ValidationErrorDetail(field="entry", code="required_field", message="Bundle must contain entries"))
        for idx, entry in enumerate(entries):
            resource = (entry or {}).get("resource") or {}
            errors.extend(
                ValidationErrorDetail(
                    field=f"entry[{idx}].{e.field}",
                    code=e.code,
                    message=e.message,
                )
                for e in validate_fhir(resource)
            )
    else:
        errors.append(ValidationErrorDetail(field="resourceType", code="unsupported", message=f"Unsupported resourceType: {resource_type}"))
    return errors


def validate_payload(source: InteropSource, payload: dict[str, Any]) -> list[ValidationErrorDetail]:
    validators = {
        InteropSource.OPENMRS: validate_openmrs,
        InteropSource.OPENELIS: validate_openelis,
        InteropSource.DHIS2: validate_dhis2,
        InteropSource.FHIR: validate_fhir,
    }
    return validators[source](payload)


def extract_external_id(source: InteropSource, payload: dict[str, Any]) -> str:
    if source == InteropSource.OPENMRS:
        return str(payload["uuid"])
    if source == InteropSource.OPENELIS:
        return str(payload["accessionNumber"])
    if source == InteropSource.DHIS2:
        return f"{payload['dataSet']}:{payload['orgUnit']}:{payload['period']}"
    if source == InteropSource.FHIR:
        if payload.get("resourceType") == "Bundle":
            first = (payload.get("entry") or [{}])[0].get("resource") or {}
            return str(first.get("id", payload.get("id", "bundle-unknown")))
        return str(payload.get("id", "unknown"))
    return "unknown"
