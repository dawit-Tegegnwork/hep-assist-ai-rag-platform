# Product preferences

Living clinician/product preferences for MediMind / Hep Assist. Prefer short, enforceable rules over essays.

## Clinical summary (2026-11-09 — Hermona Addisu)

- Disease / display names only inside the clinical summary — never ICD-11 codes (e.g. prefer "intervertebral disc degeneration", not "FA80- - - Intervertebral disc degeneration").
- If a chart field is not documented, omit that clause or block entirely. Do not narrate absence ("not documented", "not recorded").
- If onset/time is missing, omit time wording entirely.
- If a section (symptoms, vitals, exam, etc.) has no real documented values, omit the whole section.
- Keep summaries short; prefer compression over exhaustive filler.

## Encounter / Copilot draft UI (2026-11-09 — Hermona Addisu)

- On the encounter surface where findings and the clinical summary are already shown, do not show a draft text box or a Draft button — those controls are confusing and unused.
- Full assessment draft editing stays on the dedicated Assess tab only.
- **Note-tab SOAP textareas are not Hermona’s Draft UI.** They are optional voice→Bahmni capture helpers. Keep them hidden until the clinician records or explicitly chooses “Show SOAP fields,” so empty SOAP does not look like a second unused draft when chart findings already exist.

## Voice / Record (2026-11-09)

- Browsers block `getUserMedia` on non-secure origins. LAN Bahmni on `http://…:9180` cannot use the mic.
- One-step fix on this lab: open the same chart on `https://<host>:9543` (accept the cert once), allow the microphone, then press Record.
- Copilot Note tab should surface that HTTPS path as the primary CTA when the page is insecure.
