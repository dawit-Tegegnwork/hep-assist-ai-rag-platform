# Healthcare Interoperability Modernization Lab

**Author:** Dawit Wubale  
**Type:** Synthetic integration / customization portfolio lab  
**Status:** Demo and learning project — not production integration

## What problem this solves

Health programs in low-resource settings often run **multiple digital systems** that do not share a single data model:

- **OpenMRS** (and distributions like **Bahmni**) for clinical encounters
- **OpenELIS** for laboratory orders and results
- **DHIS2** for aggregate program reporting
- **FHIR** / **HL7-style** messaging as emerging exchange standards

Real deployments need **validation, transformation, audit trails, and safe hand-offs** between these shapes of data. This lab demonstrates that Dawit can work **around** those ecosystems — designing adapters, canonical models, and operational visibility — without falsely claiming he built OpenMRS, OpenELIS, or DHIS2 themselves.

## What systems this simulates (honest framing)

| System | What we simulate | What we do **not** claim |
|--------|------------------|---------------------------|
| OpenMRS | REST-like patient + encounter + obs JSON | Running or modifying OpenMRS core |
| OpenELIS | Lab accession + test result payloads | Live LIS connectivity |
| DHIS2 | Aggregate `dataValues` report shape | DHIS2 server or metadata sync |
| FHIR R4-like | Patient, Observation, Bundle examples | Certified FHIR server |
| Bahmni | Referenced in docs as OpenMRS distribution context | Bahmni deployment |

All payloads are **synthetic**. No patient data. No connection to hospital networks.

## What Dawit built / customized

1. **FastAPI interoperability API** — ingest, validate, transform, export, audit
2. **Source adapters** — OpenMRS-, OpenELIS-, DHIS2-, and FHIR-inspired mappings to a canonical bundle
3. **Validation layer** — required fields, invalid dates, duplicate IDs, missing lab fields
4. **Audit log** — payload received → validation → transformation → export
5. **Operations dashboard** — message counts, failures, exports, latest events
6. **Documentation** — interoperability map, ecosystem notes, FHIR/HL7 learning notes, deployment runbook
7. **Automated tests** — valid/invalid payloads, transformation, audit trail, duplicate detection

## Run in 5 minutes (recruiters)

```bash
git clone <repo-url>
cd medimind-hep-assist-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
cd backend && PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
./scripts/interop_demo.sh http://127.0.0.1:8000
```

| Resource | URL |
|----------|-----|
| Interop dashboard | http://localhost:8000/interop/dashboard |
| OpenAPI (interop tag) | http://localhost:8000/docs#/interop |
| Sample OpenMRS payload | `GET /api/v1/interop/samples/openmrs` |
| Ingest + export | `POST /api/v1/interop/ingest/{source}` |

Or with Docker (full platform including RAG):

```bash
docker compose up --build
# Interop API at http://localhost:8000/api/v1/interop/...
```

Sample payload files (for curl/file-based demos): `interop-lab/data/samples/`.

## Synthetic data notice

Every patient name, identifier, lab value, and aggregate count in this lab is **fabricated for demonstration**. Do not use with PHI. Do not present this repo as a deployed national HMIS or live Bahmni integration.

## API overview

```
GET  /api/v1/interop/sources
GET  /api/v1/interop/samples/{source}?variant=valid|invalid
POST /api/v1/interop/ingest/{source}     # body: source-specific JSON
POST /api/v1/interop/messages/{id}/export
GET  /api/v1/interop/dashboard/stats
GET  /api/v1/interop/audit
GET  /api/v1/interop/messages/{id}
```

## Further reading

- [docs/interoperability-map.md](../docs/interoperability-map.md)
- [docs/openmrs-openelis-dhis2-notes.md](../docs/openmrs-openelis-dhis2-notes.md)
- [docs/fhir-hl7-learning-notes.md](../docs/fhir-hl7-learning-notes.md)
- [docs/deployment-runbook.md](../docs/deployment-runbook.md)
