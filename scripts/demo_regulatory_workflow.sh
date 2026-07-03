#!/usr/bin/env bash
# Regulatory workflow demo — full transition path with audit verification.
# Usage: ./scripts/demo_regulatory_workflow.sh [BASE_URL]
set -euo pipefail

BASE="${1:-http://127.0.0.1:8000}"
API="$BASE/api/v1"

echo "== eRIS Modernization Lab — regulatory workflow demo =="
echo "Base URL: $BASE"

echo "1. Health ready"
curl -sf "$BASE/health/ready" | head -c 200
echo ""

login() {
  local user="$1" pass="$2"
  curl -sf -X POST "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$user\",\"password\":\"$pass\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}

echo "2. Applicant login"
APPLICANT_TOKEN=$(login applicant applicant123)

echo "3. Submit application"
APP_ID=$(curl -sf -X POST "$API/regulatory/applications" \
  -H "Authorization: Bearer $APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Demo Workflow Product",
    "application_type": "marketing_authorization",
    "applicant_organization": "Synthetic Pharma Ltd",
    "dossier_summary": "Automated demo dossier with sufficient detail for regulatory workflow testing.",
    "supporting_documents": ["demo_module.pdf"]
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "   Application ID: $APP_ID"

echo "4. Reviewer login + start technical review"
REVIEWER_TOKEN=$(login reviewer reviewer123)
curl -sf -X POST "$API/regulatory/applications/$APP_ID/transition" \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"start_technical_review","comment":"Demo assignment"}' > /dev/null

echo "5. Request clarification"
curl -sf -X POST "$API/regulatory/applications/$APP_ID/transition" \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"request_clarification","comment":"Need stability appendix"}' > /dev/null

echo "6. Applicant resubmit"
curl -sf -X POST "$API/regulatory/applications/$APP_ID/resubmit" \
  -H "Authorization: Bearer $APPLICANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dossier_summary": "Updated dossier including stability appendix for demo.",
    "supporting_documents": ["demo_module.pdf","stability.pdf"],
    "applicant_note": "Addressed clarification"
  }' > /dev/null

echo "7. Resume review and approve"
curl -sf -X POST "$API/regulatory/applications/$APP_ID/transition" \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"start_technical_review","comment":"Re-opened"}' > /dev/null
curl -sf -X POST "$API/regulatory/applications/$APP_ID/transition" \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","comment":"Synthetic demo approval"}' > /dev/null

echo "8. Dashboard summary"
curl -sf "$API/regulatory/dashboard/summary" \
  -H "Authorization: Bearer $REVIEWER_TOKEN"
echo ""

echo "9. Audit trail"
AUDIT_COUNT=$(curl -sf "$API/regulatory/applications/$APP_ID/audit" \
  -H "Authorization: Bearer $(login auditor auditor123)" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "   Audit events: $AUDIT_COUNT"

if [ "$AUDIT_COUNT" -lt 3 ]; then
  echo "ERROR: Expected at least 3 audit events" >&2
  exit 1
fi

echo "Done — regulatory workflow demo completed successfully."
