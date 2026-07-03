# Local Language Support — HEP Assist AI

**Honest scope:** Amharic **examples** for architecture discussion · **not** full multilingual production

## What this repo demonstrates

| Feature | Status |
|---------|--------|
| Amharic synthetic guideline chunks | `backend/app/data/synthetic_guidelines_am.md` |
| `language: "am"` on questions | API + UI |
| Language-filtered retrieval | `VectorRetriever.search(..., language="am")` |
| Amharic answer template (mock LLM) | Mixed Amharic/English with disclaimer |
| Risk flags `local_language_demo`, `not_certified_translation` | On Amharic answers |
| Amharic unsafe question patterns (prescribing/diagnosis examples) | `safety.py` |
| Certified translation | **Not included** |
| Speech (STT/TTS) / IVR | **Documented only** |
| Cross-lingual retrieval | **Not included** |

## Content disclaimer

Amharic snippets are **fabricated portfolio examples**. The file header states they are not clinical guidance or certified translations. UI and API responses repeat this.

## Example questions (UI)

**Safe (screening):**

```
የሂፓታይቲስ B ምርመራ በcommunity setting እንዴት ይደረጋል?
```

**Unsafe (prescribing — should refuse):**

```
ለሂፓታይቲስ C ታዳሚ antiviral መድሃኒት መጠን ይመድቡልኝ
```

## Retrieval behavior

- Queries with `language: "am"` search **Amharic chunks only** in this demo.
- Production systems might: detect language → translate query for retrieval → answer in worker's language. That pipeline is **not** built here.

## Safety limitations for Amharic

- English regex patterns cover most unsafe cases in EN questions.
- Amharic adds **example** patterns for prescribing/diagnosis keywords; not exhaustive.
- Grounding heuristic (`assess_answer_grounding`) is Latin-token based — weak for Amharic script.

## Voice / IVR future path (discussion only)

```
Caller (Amharic) → Whisper STT → language detect
  → RAG Q&A (this API) → Amharic TTS → audio response
  → SMS fallback: cited excerpt when bandwidth is low
```

## Production checklist (not done)

- [ ] Certified translation of approved ministry content
- [ ] Locale-specific unsafe pattern sets + clinician review
- [ ] Embedding model evaluated on Amharic retrieval quality
- [ ] Human review by bilingual clinicians
- [ ] Community testing for comprehension and trust

## Related

- [Offline-first design](offline-first-design.md)
- [AI safety case](ai-safety-case.md)
- [Interview demo script](interview-demo-script.md)
