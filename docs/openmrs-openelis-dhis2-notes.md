# OpenMRS, OpenELIS, DHIS2 — Ecosystem Notes (Lab Context)

Notes for recruiters and interviewers reviewing Dawit's interoperability lab. These systems are **referenced for realism**; this repo does **not** contain their source code or live integrations.

## OpenMRS

**What it is:** Open-source electronic medical record platform widely used in Africa and Asia.

**Typical concepts:**

- **Patient** — `uuid`, identifiers, person demographics
- **Encounter** — visit container with datetime and type
- **Obs** — observations (vitals, diagnoses, custom concepts)

**What Dawit's lab does:** Accepts JSON shaped like simplified OpenMRS REST responses, validates required patient/encounter fields, maps `obs` into canonical encounters.

**What Dawit does not claim:** Writing OpenMRS modules, deploying OpenMRS servers, or maintaining OpenMRS core.

## Bahmni (related)

**What it is:** OpenMRS-based distribution for hospitals/clinics, often paired with lab and billing components.

**Lab relevance:** Bahmni deployments commonly need **middleware** between OpenMRS, OpenELIS, and reporting tools. This lab models that middleware layer — validation, transformation, audit — not Bahmni UI or configuration.

## OpenELIS

**What it is:** Open-source laboratory information system.

**Typical concepts:**

- **Accession number** — unique lab order identifier
- **Test panel / analyte** — coded tests with numeric or text results
- **Result status** — preliminary, final, corrected

**What Dawit's lab does:** Validates accession + patient linkage, ensures each `testResults[]` entry has code, name, and value, maps to canonical `lab_results`.

**What Dawit does not claim:** HL7 v2 instrument interfaces, ASTM connectivity, or OpenELIS fork maintenance.

## DHIS2

**What it is:** Open-source health management information system for aggregate reporting (HIV, TB, immunization, etc.).

**Typical concepts:**

- **Data set** — form template for a reporting period
- **Organisation unit** — facility or district
- **Data element** — indicator field
- **Period** — often `YYYYMM` or daily `YYYYMMDD`

**What Dawit's lab does:** Validates aggregate payloads, maps `dataValues` to canonical `aggregate_reports`.

**What Dawit does not claim:** DHIS2 app development, metadata publishing, or national tracker deployments.

## Integration patterns in real programs

| Pattern | Example | Lab equivalent |
|---------|---------|----------------|
| Point-to-point REST | Bahmni → custom middleware → OpenELIS | `POST /interop/ingest/openelis` |
| Batch aggregate upload | Facility → DHIS2 | `POST /interop/ingest/dhis2` |
| Clinical + lab correlation | Match patient IDs across systems | Canonical bundle links `patient_external_id` |
| Audit for compliance | Log every exchange | `interop_audit_events` table |

## Sample curl (synthetic)

```bash
# OpenMRS-style ingest
curl -X POST http://localhost:8000/api/v1/interop/ingest/openmrs \
  -H "Content-Type: application/json" \
  -d @<(curl -s http://localhost:8000/api/v1/interop/samples/openmrs)
```

## Learning resources (external)

- OpenMRS Wiki: https://openmrs.org/
- OpenELIS Global: https://openelis-global.org/
- DHIS2 Documentation: https://docs.dhis2.org/
- Bahmni: https://www.bahmni.org/
