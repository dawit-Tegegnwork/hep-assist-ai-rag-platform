# FHIR & HL7-Style Workflow Learning Notes

Context for Dawit's interoperability lab — educational notes, not certification claims.

## FHIR in this lab

[FHIR](https://hl7.org/fhir/) (Fast Healthcare Interoperability Resources) is HL7's modern REST-friendly standard. This lab includes **FHIR-inspired** JSON for:

| Resource | Lab usage |
|----------|-----------|
| `Patient` | Demographics normalization |
| `Observation` | Lab-like results (`valueQuantity`) |
| `Bundle` | Multi-resource ingest (patient + obs) |

### Example (synthetic Patient)

```json
{
  "resourceType": "Patient",
  "id": "fhir-patient-001-synthetic",
  "name": [{"family": "Tadesse", "given": ["Helen"]}],
  "gender": "female",
  "birthDate": "1988-07-22"
}
```

### What Dawit implemented

- Validation of required Patient/Observation fields
- Bundle expansion and per-resource validation
- Mapping Observation `valueQuantity` → canonical `lab_results`
- Preserving raw FHIR resources in `fhir_resources[]` on export

### What Dawit does not claim

- FHIR R4 conformance statement
- SMART on FHIR authorization
- Terminology services (SNOMED, LOINC binding)
- Production HAPI FHIR or Google Healthcare API deployment

## HL7 v2 (conceptual)

Classic **HL7 v2** messages (e.g. `ORM^O01` orders, `ORU^R01` results) are still common for lab instruments. This lab uses **JSON** rather than pipe-delimited v2, but the **workflow concepts** align:

| HL7 v2 concept | Lab analogue |
|----------------|--------------|
| PID segment | Patient identifiers in OpenMRS / FHIR Patient |
| OBR segment | Order / accession in OpenELIS |
| OBX segment | Result value in `testResults` or Observation |
| MSH segment | Message metadata → audit `payload_received` |

A production bridge would add an HL7 v2 parser (e.g. HAPI) before the same validation and canonical mapping used here.

## FHIR vs proprietary REST (OpenMRS)

| Aspect | OpenMRS-style JSON | FHIR Patient |
|--------|-------------------|--------------|
| ID field | `uuid` | `id` |
| Name | `person.givenName` | `name[].given` |
| Birth date | `person.birthdate` | `birthDate` |
| Observations | `encounters[].obs` | Separate `Observation` resources |

Dawit's **adapters** exist precisely to bridge these shapes into one canonical model.

## Recommended learning path

1. Read FHIR Patient and Observation overviews on hl7.org
2. Run this lab's `POST /interop/ingest/fhir` with bundle sample
3. Compare canonical export to OpenMRS ingest for same synthetic patient storyline
4. Review audit log for traceability (`GET /api/v1/interop/audit`)

## API quick reference

```bash
# FHIR bundle sample
curl http://localhost:8000/api/v1/interop/samples/fhir

# Ingest
curl -X POST http://localhost:8000/api/v1/interop/ingest/fhir \
  -H "Content-Type: application/json" \
  -d '{"resourceType":"Bundle", ...}'
```

## Honest portfolio framing

> "I built a synthetic interoperability lab that validates and transforms payloads **inspired by** OpenMRS, OpenELIS, DHIS2, and FHIR — demonstrating adapter design, audit logging, and operational dashboards. I have not claimed to build those platforms; I show I can integrate **around** them safely."
