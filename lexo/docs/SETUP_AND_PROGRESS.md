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

---

## 3. Ticket status (code today)

Mark **DONE** only if the implementation exists in the repo. Everything else is not done.

| Ticket | Title | Status | Evidence in repo |
|---|---|---|---|
| **TKT-001** | Backend config & env foundation | **DONE** | `config.py` (`Settings` + validators), CORS from `settings.cors_origins`, `.env.example` (`GEMINI_API_KEY`, `JWT_SECRET`, `DATABASE_URL`, `UPLOAD_DIR`, …), deps in `requirements.txt` |
| **TKT-002** | Data models & DB setup (SQLModel) | **DONE** | `models/tables.py` (8 tables), `db.py` (engine, `get_session`, `create_db_and_tables`), lifespan `create_all` in `main.py`, Neon-only `DATABASE_URL` |
| **TKT-003** | Object storage helper | **DONE** (local-disk path) | `services/storage.py`: `upload_file` / `read_file` / `delete_file`; `get_signed_url` → `NotImplementedError` + TODO for later S3 |
| **TKT-004** | Auth backend: signup + login (JWT) | **DONE** | `routes/auth.py` + `services/auth_service.py`: `POST /api/auth/signup`, `POST /api/auth/login`; bcrypt + PyJWT (~15 min access token) |
| **TKT-005** | Auth refresh + logout | **DONE** | Signup/login issue `refresh_token` (hashed in `refresh_tokens`); `POST /api/auth/refresh`, `POST /api/auth/logout`; `get_current_user` Bearer dependency |
| **TKT-006+** | Auth/upload/dashboard frontend, analyze, voice, deploy, … | **Not done** | See checklist below |
| **TKT-007** | Upload backend | **DONE** | `POST /api/upload`: JWT + multipart PDF/DOCX + `doc_type`, `storage.upload_file`, `documents` row `status=uploaded`, returns `document_id` |
| **TKT-008** | Documents list + status | **DONE** | `GET /api/documents`, `GET /api/documents/{id}` (owner-scoped; cross-user → 404); `status` + `risk_score` (null until report) |
| Analyze / voice stubs | Pipeline + voice | **Not done** | `POST /api/analyze`, `POST /api/voice` return **501** |
| Frontend | Next.js screens | **Not done** | Placeholder home only (`app/page.tsx`: “Coming soon”) |

---

## 4. Relevant file map

```
lexo/
  backend/
    main.py                 # FastAPI app, CORS, lifespan → create_all, router includes, GET /health
    config.py               # pydantic-settings Settings (DATABASE_URL, JWT_SECRET, UPLOAD_DIR, …)
    db.py                   # Neon engine, get_session, create_db_and_tables
    requirements.txt
    .env.example            # copy → .env (never commit .env)
    .env                    # local secrets (gitignored)
    models/
      tables.py             # SQLModel: users, documents, reports, flags, citations,
                            #             missing_clauses, action_items, refresh_tokens
      schemas.py            # API: auth tokens, UploadResponse, DocumentRead, Report/Flag/Citation
    routes/
      auth.py               # signup, login, refresh, logout  ✅
      upload.py             # POST /api/upload  ✅
      documents.py          # GET /api/documents, GET /api/documents/{id}  ✅
      analyze.py            # POST /api/analyze → 501 stub
      voice.py              # POST /api/voice → 501 stub
    services/
      auth_service.py       # hash/verify, JWT, refresh tokens, get_current_user
      document_service.py   # upload validation + document create/list/get
      storage.py            # local-disk upload_file / read_file / delete_file
    uploads/                # created on first storage write (UPLOAD_DIR)
  frontend/
    app/page.tsx            # placeholder only
    .env.local.example      # NEXT_PUBLIC_API_URL=http://localhost:8000
  docs/
    SETUP_AND_PROGRESS.md   # this file
    FEATURE_TICKETS.md
    SYSTEM_DESIGN.md
    PRD.md
    SECURITY_AND_ACCESS.md
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
| `DATABASE_URL` | Neon **pooled** URL, e.g. `postgresql://USER:PASSWORD@HOST/DB?sslmode=require` |
| `JWT_SECRET` | Long random string (required; app will not start if empty). Example: `openssl rand -hex 32`, or in PowerShell: `-join ((1..64) \| ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })` |
| `CORS_ORIGINS` | Keep `["http://localhost:3000"]` for local Next.js |
| `UPLOAD_DIR` | Keep `./uploads` unless you need another path |
| API keys (`GEMINI_*`, `EXA_*`, …) | Can stay empty until analyze/voice tickets |

5. **Never commit `.env`.** It is listed in `lexo/.gitignore`. Commit only `.env.example`.

`DATABASE_URL` notes:

- Prefer Neon’s **pooled** string from the console.
- `postgres://` is normalized to `postgresql://` in `config.py`.
- Missing/empty `DATABASE_URL` or `JWT_SECRET` fails at import/boot with a clear validator error — there is no SQLite default.

---

## 6. Run the backend (Windows PowerShell)

From a fresh shell:

```powershell
cd c:\Users\Dell\Downloads\cursor-ahm\lexo\backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn main:app --reload
```

Default URL: **http://127.0.0.1:8000**

If execution policy blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Frontend is not required yet for backend work. When you need it later:

```powershell
cd c:\Users\Dell\Downloads\cursor-ahm\lexo\frontend
Copy-Item .env.local.example .env.local
npm install
npm run dev
```

---

## 7. How to verify

| Check | How |
|---|---|
| Health | Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"ok"}` |
| OpenAPI / Swagger | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — auth, upload, documents, plus analyze/voice 501 stubs |
| Auth smoke test | **signup** / **login** → `access_token` + `refresh_token`; **refresh** with refresh token → new access; **logout** (Bearer + refresh body) → later refresh → 401 |
| Upload smoke test | Authorize with access token → **POST /api/upload** (PDF/DOCX + `doc_type`) → `document_id`; file under `UPLOAD_DIR`; Neon `documents` row `status=uploaded` |
| Documents smoke test | **GET /api/documents** → current user’s docs newest first; **GET /api/documents/{id}** for own id works; another user’s id → **404** (not 403) |
| Neon tables after boot | `users`, `documents`, `reports`, `flags`, `citations`, `missing_clauses`, `action_items`, `refresh_tokens` |
| Still stubs | `POST /api/analyze`, `POST /api/voice` → **501** |

---

## 8. What’s next (suggested order)

Foundation through upload + document list is in place. Continue Phase 1:

1. **Frontend** — **TKT-006** login/signup UI (store access + refresh), then **TKT-009** upload page and **TKT-010** dashboard list.
2. Then Phase 2+ per [`FEATURE_TICKETS.md`](./FEATURE_TICKETS.md) (extract → Gemini analyze → report → grounding → voice).

Do not start analyze/voice UI while frontend auth/upload are still placeholders.

---

## 9. Checklist — done vs not done

### Done

- [x] `Settings` + `.env` / `.env.example` contract (`DATABASE_URL`, `JWT_SECRET`, `UPLOAD_DIR`, API key placeholders)
- [x] CORS for `http://localhost:3000` (credentials allowed; origins not `*`)
- [x] Neon Postgres via SQLModel; `create_all` on startup; 8 tables
- [x] Local-disk `services/storage.py`
- [x] `POST /api/auth/signup` + `POST /api/auth/login` (JWT access + refresh tokens)
- [x] `POST /api/auth/refresh` + `POST /api/auth/logout` (`TKT-005`)
- [x] `get_current_user` Bearer access JWT dependency
- [x] Real `POST /api/upload` (`TKT-007`)
- [x] `GET /api/documents` + `GET /api/documents/{id}` (`TKT-008`)
- [x] `GET /health`

### Not done

- [ ] Analyze pipeline (`TKT-014`…); `/api/analyze` still 501
- [ ] Voice (`TKT-028`…); `/api/voice` still 501
- [ ] Frontend beyond placeholder home (`TKT-006`, `TKT-009`, `TKT-010`, …)
- [ ] Deploy / rate limits / delete hardening (Phase 5)

---

## 10. Related docs

| Doc | Link |
|---|---|
| Feature tickets / backlog | [`FEATURE_TICKETS.md`](./FEATURE_TICKETS.md) |
| Architecture, data model, API contract | [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) |
| Product requirements | [`PRD.md`](./PRD.md) |
| Access control & security acceptance | [`SECURITY_AND_ACCESS.md`](./SECURITY_AND_ACCESS.md) |
