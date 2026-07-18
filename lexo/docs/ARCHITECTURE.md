# Lexo Architecture

Lexo follows a linear pipeline from client to report output.

```
Client (Next.js)
    → API (FastAPI)
    → Parser / OCR
    → LLM analysis
    → Exa grounding
    → Storage
    → Report output
```

## Flow

1. **Client** — The Next.js frontend lets users upload documents and view analysis reports.
2. **API** — FastAPI receives uploads and analysis requests, orchestrates the pipeline, and returns structured JSON.
3. **Parser / OCR** — Extracted text is pulled from PDFs and scanned documents so the model can reason over clause content.
4. **LLM analysis** — An LLM reviews the document text for risk flags, missing clauses, and action items, producing the shared report contract (`risk_score`, `flags`, `missing_clauses`, `action_items`).
5. **Exa grounding** — Exa is used to ground citations and supporting references against external legal/context sources.
6. **Storage** — Results and metadata are persisted (PostgreSQL) for later retrieval.
7. **Report output** — The structured report is returned to the client for display.

## Optional voice path

- **Voice-in (Wispr Flow):** Spoken questions or dictation can be transcribed and routed into the same API surface.
- **Voice-out (ElevenLabs):** Report summaries or key findings can be spoken back to the user.

These voice integrations are optional and sit alongside the core upload → analyze → report path; they do not replace it.
