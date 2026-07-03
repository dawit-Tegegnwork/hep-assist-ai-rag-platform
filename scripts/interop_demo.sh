#!/usr/bin/env bash
# Interoperability lab demo — synthetic payloads only.
set -euo pipefail

BASE="${1:-http://127.0.0.1:8000}"
API="${BASE}/api/v1/interop"

echo "=== Healthcare Interoperability Lab Demo ==="
echo "Base URL: ${BASE}"
echo ""

echo "1. List sources"
curl -s "${API}/sources" | python3 -m json.tool
echo ""

echo "2. Fetch OpenMRS sample (valid)"
OPENMRS=$(curl -s "${API}/samples/openmrs")
echo "${OPENMRS}" | python3 -m json.tool | head -20
echo "   ..."

echo ""
echo "3. Ingest OpenMRS payload"
INGEST=$(curl -s -X POST "${API}/ingest/openmrs" -H "Content-Type: application/json" -d "${OPENMRS}")
echo "${INGEST}" | python3 -m json.tool
MSG_ID=$(echo "${INGEST}" | python3 -c "import sys,json; print(json.load(sys.stdin)['message_id'])")

echo ""
echo "4. Export canonical JSON"
curl -s -X POST "${API}/messages/${MSG_ID}/export" | python3 -m json.tool | head -25
echo "   ..."

echo ""
echo "5. Ingest OpenELIS + DHIS2 + FHIR samples"
for src in openelis dhis2 fhir; do
  PAYLOAD=$(curl -s "${API}/samples/${src}")
  curl -s -X POST "${API}/ingest/${src}" -H "Content-Type: application/json" -d "${PAYLOAD}" > /dev/null
  echo "   ✓ ${src}"
done

echo ""
echo "6. Invalid payload (validation failure)"
INVALID=$(curl -s "${API}/samples/openmrs?variant=invalid")
curl -s -X POST "${API}/ingest/openmrs" -H "Content-Type: application/json" -d "${INVALID}" | python3 -m json.tool

echo ""
echo "7. Duplicate detection (re-ingest same OpenMRS id)"
HTTP=$(curl -s -o /tmp/dup.json -w "%{http_code}" -X POST "${API}/ingest/openmrs" -H "Content-Type: application/json" -d "${OPENMRS}")
echo "   HTTP ${HTTP}"
cat /tmp/dup.json | python3 -m json.tool

echo ""
echo "8. Dashboard stats"
curl -s "${API}/dashboard/stats" | python3 -m json.tool

echo ""
echo "Done. Open dashboard: ${BASE}/interop/dashboard"
