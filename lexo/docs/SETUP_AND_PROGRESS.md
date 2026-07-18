# Lexo — Setup & Progress Guide

Practical runbook for the **current** repo state (inspected against `lexo/backend/` and `lexo/frontend/`). Ticket IDs match [`FEATURE_TICKETS.md`](./FEATURE_TICKETS.md).

---

## 1. What Lexo is

Lexo is an AI legal-document assistant for everyday people in India reviewing **rental** and **employment** agreements. A user uploads a PDF/DOCX, Lexo flags risky or missing terms, grounds citations (or labels them unverified), and returns a plain-language risk report — with optional voice summary/Q&A later. It is **not** a substitute for a lawyer; every report carries a “not legal advice” disclaimer.

---

## 2. Locked decisions (do not reopen mid-hackathon)

| Decision | Choice | Notes |
|---|---|---|
| Database | **Neon Postgres Serverless** | Required `DATABASE_URL` (pooled, `sslmode=require`). **No SQLite fallback.** |
| File storage | **Local disk** via `UPLOAD_DIR` | `services/storage.py` writes under `./uploads` (configurable). Not S3/`boto3` for MVP. `get_signed_url` is intentionally unimplemented. |
| Build order | **Backend-first** | Confirm shapes in `/docs`, then wire the frontend. |
| Layout | **Top-level `lexo/backend/`** | Keep `main.py`, `config.py`, `db.py`, `routes/`, `models/`, `services/` at the backend root — do **not** restructure into `app/`. |
| Voice STT (TKT-027) | **Browser Web Speech API** | Wispr unused. No `WISPR_API_KEY`. No server-side STT. Backend gets **text** questions only (`/api/voice/ask`). Chrome = demo browser. |
| Rate limits (TKT-035) | **20 uploads / 10 analyze / user / hour** | In-memory counters (TKT-036); no Redis. |

---

## 3. Ticket status (code today)

Mark **DONE** only if the implementation exists in the repo. Everything else is not done.

| Ticket | Title | Status | Evidence in repo |
|---|---|---|---|
| **TKT-001** | Backend config & env foundation | **DONE** | `config.py` (`Settings` + validators), CORS from `settings.cors_origins`, `.env.example`, deps in `requirements.txt` |
| **TKT-002** | Data models & DB setup (SQLModel) | **DONE** | `models/tables.py` (8 tables), `db.py`, lifespan `create_all` in `main.py` |
| **TKT-003** | Object storage helper | **DONE** (local-disk path) | `services/storage.py` |
| **TKT-004** | Auth backend: signup + login (JWT) | **DONE** | `routes/auth.py` + `services/auth_service.py` |
| **TKT-005** | Auth refresh + logout | **DONE** | refresh/logout + `get_current_user` |
| **TKT-006+** | Auth/upload/dashboard frontend | **Not done** | Frontend still placeholder |
| **TKT-007** | Upload backend | **DONE** | `POST /api/upload` (+ rate limit TKT-036) |
| **TKT-008** | Documents list + status | **DONE** | `GET /api/documents`, `GET /api/documents/{id}` (+ optional `report_id`) |
| **TKT-014** | Text extraction service | **DONE** | `services/extraction.py` |
| **TKT-015** | Gemini analysis service | **DONE** | `services/llm.py` → `AnalysisResult` |
| **TKT-016** | Analyze pipeline orchestration | **DONE** | `POST /api/analyze/{document_id}` + `services/analyze_service.py` BackgroundTasks; statuses `extracting` → `analyzing` → `grounding` → `analyzed` / `failed` |
| **TKT-017** | Report persistence + GET report | **DONE** | Persist Report/Flag/MissingClause/ActionItem; `GET /api/reports/{id}`; `DocumentRead.report_id` for polling navigation |
| **TKT-023** | Exa grounding service | **DONE** (lean) | `services/grounding.py`: Exa REST via httpx; trusted domains; max 3 flags; missing_clauses skipped; unverified fallback without fabricating URLs |
| **TKT-024** | Wire grounding + persist citations | **Partial** | Citations persisted on flags during analyze; no separate refactor. UI badges still frontend (TKT-025). |
| **TKT-027** | STT path decision (OQ-1) | **DONE** (docs) | Web Speech; `/api/voice/transcribe` → 501 |
| **TKT-028** | TTS backend: ElevenLabs `speak` | **DONE** | `POST /api/voice/speak` → `audio/mpeg`; `services/voice.py` via httpx; 503 if no `ELEVENLABS_API_KEY` |
| **TKT-029** | STT `transcribe` 501 contract | **DONE** | Explicit 501; Web Speech is primary |
| **TKT-030** | Voice Q&A backend | **DONE** | `POST /api/voice/ask` + `llm.answer_question`; report-scoped; JWT; `{answer, disclaimer}` |
| **TKT-035** | Rate-limit thresholds | **DONE** (docs) | 20 uploads / 10 analyze per user per hour |
| **TKT-036** | Rate limiting on upload/analyze | **DONE** | `services/rate_limit.py` in-memory deps on upload + analyze → 429 |
| **TKT-037** | Delete flow (backend half) | **DONE** (backend) | `DELETE /api/documents/{id}` cascade + blob; 204; frontend delete UI still open |
| Frontend / deploy | … | **Not done** | Voice UI, dashboard, report page, Render deploy |

---

## 4. Relevant file map

```
lexo/
  backend/
    main.py                 # FastAPI app, CORS, lifespan → create_all, routers, GET /health
    config.py               # pydantic-settings Settings
    db.py                   # Neon engine, get_session, create_db_and_tables
    requirements.txt        # includes httpx (Exa + ElevenLabs TTS)
    .env.example
    models/
      tables.py
      schemas.py            # + SpeakRequest, AskRequest, AskResponse
    routes/
      auth.py               ✅
      upload.py             ✅ (+ rate limit)
      documents.py          ✅ (+ DELETE)
      analyze.py            ✅ (+ rate limit)
      reports.py            ✅ GET /api/reports/{report_id}
      voice.py              ✅ speak + ask; transcribe still 501
    services/
      auth_service.py
      document_service.py   # + delete_document cascade
      storage.py
      extraction.py
      llm.py                # + answer_question
      grounding.py
      analyze_service.py
      report_service.py
      voice.py              # ElevenLabs TTS
      rate_limit.py         # in-memory upload/analyze limits
    uploads/
  frontend/
    app/page.tsx            # placeholder only
  docs/
    SETUP_AND_PROGRESS.md   # this file
    FEATURE_TICKETS.md
    SYSTEM_DESIGN.md
    …
```

---

## 5. One-time Neon + `.env` setup

1. Create a project at [https://console.neon.tech](https://console.neon.tech).
2. Copy the **pooled** connection string (include `?sslmode=require`).
3. In PowerShell, from the repo:

```powershell
cd c:\Users\Dell\Downloads\cursor-ahm\lexo\backend
Copy-Item .env.example .env
```

4. Edit `lexo/backend/.env` and set at least:

| Variable | What to put |
|---|---|
| `DATABASE_URL` | Neon **pooled** URL |
| `JWT_SECRET` | Long random string (required) |
| `GEMINI_API_KEY` | Required for analyze + `/api/voice/ask` |
| `EXA_API_KEY` | Optional — without it, pipeline still reaches `analyzed` with unverified citations |
| `ELEVENLABS_API_KEY` | Optional — required only for `/api/voice/speak` (else 503) |
| `ELEVENLABS_VOICE_ID` | Optional — defaults to Rachel |
| `CORS_ORIGINS` | Keep `["http://localhost:3000"]` |
| `UPLOAD_DIR` | Keep `./uploads` |

5. **Never commit `.env`.**

---

## 6. Run the backend (Windows PowerShell)

```powershell
cd c:\Users\Dell\Downloads\cursor-ahm\lexo\backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload
```

Default URL: **http://127.0.0.1:8000**

---

## 7. How to verify

| Check | How |
|---|---|
| Health | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"ok"}` |
| OpenAPI / Swagger | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| Auth | signup/login → Bearer `access_token` |
| Upload → analyze → report | See §7.1 below |
| Cross-user | Another user’s document/report id → **404** |
| Without `EXA_API_KEY` | Pipeline still reaches `analyzed`; flag citations `verified=false` |
| Speak | `POST /api/voice/speak` `{ "text": "..." }` → `audio/mpeg` (503 if no ElevenLabs key) |
| Ask | `POST /api/voice/ask` `{ "report_id", "question" }` → `{ "answer", "disclaimer" }` |
| Transcribe | `POST /api/voice/transcribe` → **501** (unchanged) |
| Delete | `DELETE /api/documents/{id}` → **204**; subsequent GETs → **404** |
| Rate limits | >20 uploads or >10 analyze / hour / user → **429** |

### 7.1 Swagger smoke: upload → analyze → report

1. **Authorize** with access token from signup/login.
2. **POST /api/upload** — PDF/DOCX + `doc_type` (`rental` or `employment`) → `document_id`.
3. **POST /api/analyze/{document_id}** → immediate `{"document_id","status":"extracting"}` (409 if already in progress / analyzed).
4. **GET /api/documents/{id}** poll until `status` is `analyzed` (or `failed`). When analyzed, note `report_id`.
5. **GET /api/reports/{report_id}** → `risk_score`, `summary`, `flags` (with `citations`), `missing_clauses`, `action_items`, `disclaimer`.

---

## 8. What’s next (suggested order)

1. **Frontend** — TKT-006 login, TKT-009 upload, TKT-010 dashboard (incl. delete button), TKT-019 analyze polling, TKT-020 report page (+ TKT-025 citation badges, TKT-031/032 voice UI).
2. Deploy (TKT-034) when the core FE path is demoable.

---

## 9. Checklist — done vs not done

### Done

- [x] Settings + Neon + local storage + auth + upload + documents list
- [x] Extraction (`TKT-014`) + Gemini analysis (`TKT-015`)
- [x] Analyze orchestration (`TKT-016`) — BackgroundTasks pipeline
- [x] Report persist + `GET /api/reports/{id}` (`TKT-017`) + disclaimer field
- [x] Lean Exa grounding (`TKT-023`) + citations persisted (`TKT-024` partial)
- [x] `DocumentRead.report_id` for post-analyze navigation
- [x] STT decision (`TKT-027`) — Web Speech; Wispr unused
- [x] ElevenLabs TTS (`TKT-028`) — `POST /api/voice/speak`
- [x] Voice Q&A (`TKT-030`) — `POST /api/voice/ask`
- [x] Rate limits (`TKT-036`) — upload/analyze in-memory
- [x] Delete backend (`TKT-037` half) — `DELETE /api/documents/{id}`

### Not done

- [ ] Citation UI badges (`TKT-025`)
- [ ] Voice UI (`TKT-031`, `TKT-032`)
- [ ] Frontend beyond placeholder home (`TKT-006`, `TKT-009`, `TKT-010`, `TKT-019`, `TKT-020`, …)
- [ ] Delete button on dashboard (TKT-037 frontend half)
- [ ] Deploy (TKT-034)

---

## 10. Related docs

| Doc | Link |
|---|---|
| Feature tickets / backlog | [`FEATURE_TICKETS.md`](./FEATURE_TICKETS.md) |
| Architecture, data model, API contract | [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) |
| Product requirements | [`PRD.md`](./PRD.md) |
| Access control & security acceptance | [`SECURITY_AND_ACCESS.md`](./SECURITY_AND_ACCESS.md) |
