# MediMind OPD AI — Honest Task Status (ai-lab)

Updated: 2026-11-05 · Model path: **ClinicDx** · Writeback: **OFF**  
Prior status overstated several items as Done. This file is the corrected truth.

Health today: Bahmni / API / Assess / NER / Ollama / KB = **6/6 OK** (host RAM tight; ClinicDx on CPU ~1–3 min)

---

## Setup & model selection

| Task | Status | Truth |
|------|--------|-------|
| Setup server & configure models on Ollama | **Done** | ai-lab Ollama + `clinicdx:latest` |
| Evaluate Meditron 7B | **Done** | Compared; lost |
| Evaluate MedGemma 4B / fine-tuned | **Done** | ClinicDx = fine-tuned MedGemma path |
| Compare models & select LLM | **Done** | ClinicDx selected for demo |

---

## Bahmni AI integration

| Task | Status | Truth |
|------|--------|-------|
| Design AI Decision Panel | **Partial** | Copilot shell matches mockups (header, urgency, vitals, History/Chat tabs, footer). Protocol ack still cosmetic. |
| Design AI components in Bahmni | **Partial** | Summary / Safety / Assess / Note / bell + Copilot EMR board. Med Infusing/Scheduled cards still thin. |
| Integrate selected LLM with Bahmni | **Done** | Proxy → `:8001` → Assess `:8321` → ClinicDx (+ orbit for chat) |
| Implement AI response handling | **Partial** | Structured Assess (`sections`, `differentials`, `urgency`) + draft editor. Clinician Bahmni Save only. |
| Panel auto-open on patient | **Done** | Auto-open + cache-bust `v=20261105ai4` |

---

## AI clinical features

| Task | Status | Truth |
|------|--------|-------|
| Patient chart summary | **Partial** | Live summary from visits/dx/labs/vitals/history. Narrative still thin when notes absent. |
| Differential diagnosis | **Partial** | Parsed into Diagnoses tab when ClinicDx returns Differential Considerations. Sometimes empty if model truncates. |
| Medical & surgical history | **Done** | History tab from chart facts (`medical` / `surgical` / `allergies`). |
| Chat feature | **Done** | In-panel Chat tab → `/copilot/{uuid}/chat` (draft-only, chart-grounded). |
| Prompt construction (create & refine) | **Partial** | 6-section ClinicDx prompt + chat mode; invent-guard still weak under thin charts. |
| Assess without Summary-first | **Done** | Assess auto-loads chart facts; no 409 Summary prerequisite. |
| Auto-draft on patient open | **Done** | Copilot auto-calls Assess once per patient when chart ready. |

---

## Clinical validation rules

| Task | Status | Truth |
|------|--------|-------|
| Build validation rules engine | **Partial** | `safety.py` dose / interaction / allergy / critical-lab. Pilot-level. |
| Allergy conflict | **Partial** | String-match; weak when allergies empty. |
| Drug interaction | **Partial** | `drug_interactions.json` when meds present. |
| Dose range checker | **Partial** | `dose_rules.json` pilot bands. |

---

## Voice

| Task | Status | Truth |
|------|--------|-------|
| Integrate STT with new model | **Not done** | Whisper path only — not ClinicDx MedASR. |
| Voice input on clinical docs | **Partial** | Record works on HTTPS `:9543` (proven getUserMedia). HTTP `:9180` blocked by browser secure-context; Note tab CTA opens HTTPS. |
| Test transcription | **Partial** | Code path exists; not demo-hardened. |

---

## Alerts, testing, quality

| Task | Status | Truth |
|------|--------|-------|
| Notifications / risk alerts | **Partial** | Bell + risk strip; Acknowledge Protocol not persisted. |
| E2E test with patient data | **Partial** | Smoke: chart warm + Assess structured + Chat OK on SEWINET (SpO2 91%, T2DM hx). |
| AI response quality checker | **Not done** | Thin-chart guard only; model can still invent labs. |
| Clinical review validation | **Not done** | Needs clinician sessions. |

---

## Extra that is actually Done

| Item | Status |
|------|--------|
| ClinicDx Assess path (`/cds/generate`) | Done |
| Chat mode on Assess engine (no forced 6-section wrap) | Done |
| WHO KB BM25 on `:4276` | Done |
| Vitals boxes = real vitals (not labs) | Done |
| Labs stay in assessment chips / safety | Done |
| `/` → Bahmni Home redirect | Done |
| Writeback OFF | Done |
| Differentials survive panel poll re-render | Done |
| Clinical summary: disease names only; omit undocumented blocks; no Draft › on encounter | Done (2026-11-09 Hermona) |

---

## Real backlog (implement next, in order)

1. Harden **invent-guard** (reject drafts that cite labs/vitals not in facts)  
2. Stabilize Assess completeness (full 6 sections every time; diffs UI always filled)  
3. AI supporter hooks beyond Clinical (Registration / Orders / Lab / IPD) — not started  
4. Allergy / drug / dose coverage on half-charts  
5. Voice E2E on ai-lab mic; MedASR later  
6. Quality checker service  
7. Clinical review + prompt refine  
8. Protocol acknowledge persistence  

---

## Demo path (what works today)

1. http://192.168.1.28:9180/bahmni/home/ → `admin` / `Admin123` → Central Triage  
2. Clinical → patient (e.g. SEWINET) → MediMind Copilot (hard-refresh once for `ai4` assets)  
3. Vitals / History tab / auto Assess draft / Diagnoses differentials when returned / Chat tab  
4. Do **not** treat Acknowledge Protocol, Voice, invent-guard, or non-Clinical Bahmni modules as finished
