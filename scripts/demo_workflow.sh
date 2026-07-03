#!/usr/bin/env bash
# End-to-end demo workflow for recruiters and interview walkthroughs.
# Usage: ./scripts/demo_workflow.sh [BASE_URL]
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
API="${BASE_URL}/api/v1"

echo "== HEP Assist AI RAG Platform — demo workflow =="
echo "Base URL: ${BASE_URL}"
echo

echo "1) Liveness"
curl -sf "${BASE_URL}/health/live" | python3 -m json.tool
echo

echo "2) Readiness (database)"
curl -sf "${BASE_URL}/health/ready" | python3 -m json.tool
echo

echo "3) Ask a safe screening question"
QUESTION_RESP=$(curl -sf -X POST "${API}/questions" \
  -H "Content-Type: application/json" \
  -d '{"question_text":"What hepatitis B screening tests are approved for community health workers?","language":"en","approved_content_only":true}')
echo "${QUESTION_RESP}" | python3 -m json.tool
QUESTION_ID=$(echo "${QUESTION_RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo

echo "4) Generate grounded answer with citations"
ANSWER_RESP=$(curl -sf -X POST "${API}/questions/${QUESTION_ID}/answer")
echo "${ANSWER_RESP}" | python3 -m json.tool
ANSWER_ID=$(echo "${ANSWER_RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo

echo "5) Human review — approve answer"
curl -sf -X POST "${API}/answers/${ANSWER_ID}/review" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","reviewer_comment":"Demo walkthrough approval"}' | python3 -m json.tool
echo

echo "6) Refusal demo — prescribing request"
UNSAFE_Q=$(curl -sf -X POST "${API}/questions" \
  -H "Content-Type: application/json" \
  -d '{"question_text":"Prescribe antiviral dose for hepatitis C patient","language":"en"}')
UNSAFE_ID=$(echo "${UNSAFE_Q}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -sf -X POST "${API}/questions/${UNSAFE_ID}/answer" | python3 -m json.tool
echo

echo "7) Amharic example question"
AM_Q=$(curl -sf -X POST "${API}/questions" \
  -H "Content-Type: application/json" \
  -d '{"question_text":"የሂፓታይቲስ B ምርመራ እንዴት ይደረጋል?","language":"am"}')
AM_ID=$(echo "${AM_Q}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -sf -X POST "${API}/questions/${AM_ID}/answer" | python3 -m json.tool
echo

echo "8) Run evaluation suite (pass/fail scoring)"
EVAL_RESP=$(curl -sf -X POST "${API}/evaluation/run")
echo "${EVAL_RESP}" | python3 -m json.tool
PASS_RATE=$(echo "${EVAL_RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('pass_rate', 0))")
echo "Pass rate: ${PASS_RATE}"
echo

echo "9) Amharic unsafe example (prescribing — should refuse)"
AM_UNSAFE=$(curl -sf -X POST "${API}/questions" \
  -H "Content-Type: application/json" \
  -d '{"question_text":"ለሂፓታይቲስ C ታዳሚ antiviral መድሃኒት መጠን ይመድቡልኝ","language":"am"}')
AM_UNSAFE_ID=$(echo "${AM_UNSAFE}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
curl -sf -X POST "${API}/questions/${AM_UNSAFE_ID}/answer" | python3 -m json.tool
echo

echo "10) Audit trail sample"
curl -sf "${API}/audit?limit=5" | python3 -m json.tool
echo

echo "11) Q&A dashboard summary"
curl -sf "${API}/dashboard/qa-summary" | python3 -m json.tool
echo
echo "Demo complete. Open ${BASE_URL}/docs and frontend at http://localhost:5173"
