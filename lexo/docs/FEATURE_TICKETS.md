# Lexo — Feature Ticket List

## 1. Document Control

| Field | Value |
|---|---|
| Status | **Draft** |
| Purpose | Actionable hackathon/MVP build backlog for Lexo, ordered by phase and dependency. |
| Related docs | [`PRD.md`](./PRD.md) (requirements, acceptance criteria, open questions), [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) (architecture, API contract, phased build plan), [`ARCHITECTURE.md`](./ARCHITECTURE.md) (high-level flow). `FRONTEND_SPEC.md` does not exist yet — frontend tickets below are derived from `PRD.md` §9 (screens) and `SYSTEM_DESIGN.md` §3.1; align with `FRONTEND_SPEC.md` if/when it's added. |
| Scope of this doc | A backlog of work items, not a PRD rewrite, API spec, or architecture doc. Do not contradict `PRD.md` / `SYSTEM_DESIGN.md`; if something here seems to conflict, the other two docs win. |

**Current build status:** every ticket below describes **work to do**, not work already done. As of this doc's drafting: the backend (`lexo/backend`) has only stub routers for `/api/upload`, `/api/analyze`, `/api/voice` that each return a bare `501 Not Implemented`; there is no auth, database, or object-storage wiring; `models/schemas.py` has only bare `Flag`/`Report` models. The frontend (`lexo/frontend`) has no screens beyond a placeholder home page. The product is **pre-Phase-1** relative to the phasing in `PRD.md` §11 / `SYSTEM_DESIGN.md` §10.

## 2. How to Use This List

- Work roughly in **Suggested Build Order** (§3) — it respects the `Depends on` column of every ticket.
- **Every feature must be demo-able end to end before moving to the next one.** Don't start Phase *N+1* tickets while Phase *N*'s checkpoint ticket is still failing.
- For any ticket marked `fullstack`, or where a backend and frontend ticket pair depend on each other: **build and confirm the backend endpoint first** (check the shape via `/docs`), *then* wire the frontend, per `.cursor/rules/general.mdc`.
- `[Decision]` and `[Spike]` tickets are non-implementation — their "acceptance criteria" is a recorded decision or finding in this document, not code. Don't skip them; they unblock the implementation tickets that depend on them.
- Priority: **P0** = needed for the next demo checkpoint · **P1** = needed for the phase to be considered complete · **P2** = nice-to-have / hardening, cut first under time pressure.

## 3. Suggested Build Order

```
TKT-001 → TKT-002 → TKT-003 → TKT-004 → TKT-006 → TKT-007 → TKT-008 → TKT-009 → TKT-010
→ TKT-005 → TKT-011 → TKT-012 → TKT-013  [Phase 1 checkpoint]
→ TKT-014 → TKT-015 → TKT-016 → TKT-017 → TKT-019 → TKT-020 → TKT-021 → TKT-018
→ TKT-022  [Phase 2 checkpoint]
→ TKT-023 → TKT-024 → TKT-025 → TKT-026  [Phase 3 checkpoint]
→ TKT-027 → TKT-028 → TKT-029 → TKT-030 → TKT-031 → TKT-032 → TKT-033  [Phase 4 checkpoint, optional]
→ TKT-034 → TKT-035 → TKT-036 → TKT-037 → TKT-038 → TKT-039 → TKT-040 → TKT-041 → TKT-042 → TKT-043
→ TKT-044  [Phase 5 checkpoint]
```

## 4. Phase Demo Checkpoints

| Phase | What "done" looks like for a live demo |
|---|---|
| **1 — Foundation** | A judge can sign up, log in, upload a PDF/DOCX with a chosen doc type, and see it appear in the dashboard with a status. No analysis yet. |
| **2 — Core analysis** | Same flow, plus clicking "Analyze" shows visible stage progress and lands on a full report page (risk badge, flags, missing clauses, action items, disclaimer). No citations yet. |
| **3 — Grounding** | The report now shows each flag/missing-clause citation visibly marked **verified** (real, linked source) or **unverified** ("general principle") — the anti-hallucination story is demoable. |
| **4 — Voice** *(optional/P1, see §6 OQ-1)* | From the report, a judge can play an audio summary and ask one spoken follow-up question, getting a grounded spoken/text answer — via Wispr Flow or a browser-based fallback. |
| **5 — Deployment & hardening** | The full flow works on the deployed Render URL, rate limits are active, deleting a document fully removes it, and `/health` + README reflect how to actually run the project. |

## 5. Ticket Index

| ID | Title | Phase | Surface | Priority | Depends on |
|---|---|---|---|---|---|
| TKT-001 | Backend config & env foundation | 1 | infra | P0 | none |
| TKT-002 | Data models & DB setup (SQLModel) | 1 | infra | P0 | TKT-001 |
| TKT-003 | Object storage helper service | 1 | backend | P0 | TKT-001 |
| TKT-004 | Auth backend: signup + login (JWT) | 1 | backend | P0 | TKT-002 |
| TKT-005 | Auth backend: refresh + logout | 1 | backend | P1 | TKT-004 |
| TKT-006 | Auth frontend: login/signup pages | 1 | frontend | P0 | TKT-004 |
| TKT-007 | Upload backend: `POST /api/upload` | 1 | backend | P0 | TKT-002, TKT-003 |
| TKT-008 | Documents backend: list + status endpoints | 1 | backend | P0 | TKT-002 |
| TKT-009 | Upload frontend: `/upload` page | 1 | frontend | P0 | TKT-007, TKT-006 |
| TKT-010 | Dashboard frontend: document list shell | 1 | frontend | P0 | TKT-008, TKT-006 |
| TKT-011 | Document status page shell (`/documents/[id]`) | 1 | frontend | P1 | TKT-008 |
| TKT-012 | [Decision] Password reset scope for MVP (OQ-6) | 1 | docs | P2 | none |
| TKT-013 | **Phase 1 demo checkpoint** | 1 | fullstack | P0 | TKT-001…011 |
| TKT-014 | Text extraction service | 2 | backend | P0 | TKT-002 |
| TKT-015 | Gemini analysis service | 2 | backend | P0 | TKT-014 |
| TKT-016 | Analyze pipeline orchestration | 2 | backend | P0 | TKT-015, TKT-008 |
| TKT-017 | Report persistence + `GET /api/reports/{id}` | 2 | backend | P0 | TKT-016 |
| TKT-018 | [Spike] Latency/SLA expectations (OQ-5) | 2 | docs | P2 | TKT-016 |
| TKT-019 | Analyze trigger + status polling UI | 2 | frontend | P0 | TKT-016, TKT-011 |
| TKT-020 | Report page UI | 2 | frontend | P0 | TKT-017 |
| TKT-021 | Disclaimer component + API field | 2 | fullstack | P0 | TKT-017, TKT-020 |
| TKT-022 | **Phase 2 demo checkpoint** | 2 | fullstack | P0 | TKT-014…021 |
| TKT-023 | Exa grounding service | 3 | backend | P0 | TKT-015 |
| TKT-024 | Wire grounding into pipeline + persist citations | 3 | backend | P0 | TKT-023, TKT-016 |
| TKT-025 | Citation UI: verified/unverified badges | 3 | frontend | P0 | TKT-020, TKT-024 |
| TKT-026 | **Phase 3 demo checkpoint** | 3 | fullstack | P0 | TKT-023…025 |
| TKT-027 | [Spike] Wispr Flow server-callable STT feasibility (OQ-1) | 4 | docs | P0 (blocker) | none |
| TKT-028 | TTS backend: ElevenLabs `speak` endpoint | 4 | backend | P1 | TKT-017 |
| TKT-029 | STT backend: `transcribe` endpoint (Wispr/fallback) | 4 | backend | P1 | TKT-027 |
| TKT-030 | Voice Q&A backend: Gemini grounded answer | 4 | backend | P1 | TKT-024, TKT-015 |
| TKT-031 | Audio summary playback UI | 4 | frontend | P1 | TKT-028, TKT-020 |
| TKT-032 | Voice Q&A UX (mic + Web Speech fallback) | 4 | frontend | P1 | TKT-029, TKT-030 |
| TKT-033 | **Phase 4 demo checkpoint** (optional) | 4 | fullstack | P1 | TKT-028…032 |
| TKT-034 | Render deployment | 5 | infra | P0 | TKT-022 |
| TKT-035 | [Decision] Rate-limit thresholds (OQ-3) | 5 | docs | P1 | none |
| TKT-036 | Rate limiting middleware on upload/analyze | 5 | backend | P1 | TKT-035 |
| TKT-037 | Delete flow | 5 | fullstack | P0 | TKT-008, TKT-010 |
| TKT-038 | [Decision] Minimal delete needed earlier than Phase 5? | 5 | docs | P1 | none |
| TKT-039 | Monitoring/health hardening | 5 | infra | P1 | TKT-034 |
| TKT-040 | [Spike] Accessibility conformance target (OQ-4) | 5 | docs | P2 | none |
| TKT-041 | [Decision] Project naming: Lexo vs VectorMinds (OQ-2) | 5 | docs | P2 | none |
| TKT-042 | README polish + `.env.example` final audit | 5 | docs | P0 | TKT-034 |
| TKT-043 | Disclaimer audit across all report surfaces | 5 | fullstack | P1 | TKT-021, TKT-025 |
| TKT-044 | **Phase 5 demo checkpoint** | 5 | fullstack | P0 | TKT-034…043 |

## 6. Tickets

### Phase 1 — Foundation

### TKT-001 — Backend config & env foundation
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | infra |
| Priority | P0 |
| Depends on | none |
| Demo value | Backend boots with centralized settings and correct env vars; unblocks every later backend ticket. |

**User / system outcome:** the backend reads all config/secrets through one `Settings` object instead of scattered `os.environ` calls, and the env-var contract matches `SYSTEM_DESIGN.md` §9.

**Scope:**
- Add a `pydantic-settings`-based `Settings` class (`database_url`, `cors_origins`, `jwt_secret`, `gemini_api_key`, `exa_api_key`, `elevenlabs_api_key`, `wispr_api_key`, `s3_endpoint`, `s3_access_key`, `s3_secret_key`, `s3_bucket`).
- Rename `LLM_API_KEY` → `GEMINI_API_KEY` in `lexo/backend/.env.example`.
- Add `JWT_SECRET`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET` to `.env.example`.
- Update `requirements.txt`: add `pydantic-settings`, `sqlmodel`, `pyjwt`, `passlib[bcrypt]`, `boto3`, `google-generativeai`, `pdfplumber`, `python-docx`.
- Wire `CORSMiddleware` using `settings.cors_origins` (must include `http://localhost:3000`).

**Out of scope:**
- Actual DB connection (TKT-002).
- Actual S3 client (TKT-003).

**Acceptance criteria:**
- [ ] `backend/.env.example` has `GEMINI_API_KEY` (not `LLM_API_KEY`), `JWT_SECRET`, and all `S3_*` vars.
- [ ] `requirements.txt` installs cleanly with the new dependencies.
- [ ] `GET /health` still returns 200 with CORS middleware active.
- [ ] CORS allows the frontend dev origin; never `allow_origins=["*"]` combined with `allow_credentials=True`.

**Notes / risks:** keep the current top-level `lexo/backend/` layout (don't restructure into `app/`) to avoid unnecessary churn — this is a deliberate deviation from the auto-attached `backend-fastapi.mdc` example structure, noted here rather than silently done.

---

### TKT-002 — Data models & DB setup (SQLModel)
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | infra |
| Priority | P0 |
| Depends on | TKT-001 |
| Demo value | `SQLModel.metadata.create_all` creates all tables on a fresh DB — foundation for every persistence ticket. |

**User / system outcome:** persisted tables exist for `users`, `documents`, `reports`, `flags`, `citations`, `missing_clauses`, `action_items`, `refresh_tokens`, matching `SYSTEM_DESIGN.md` §5.

**Scope:**
- Add SQLModel table models mirroring the §5 ER diagram, including FKs.
- `db.py`: engine + `get_session` dependency; default `sqlite:///./app.db` via `DATABASE_URL`; `create_all` on startup.
- Extend the existing `Report`/`Flag` Pydantic schemas per the §5 note (`document_id`, `summary`, `created_at`, nested `citations` with a `verified` boolean instead of a bare citation string).

**Out of scope:**
- Alembic migrations, seed/demo data.

**Acceptance criteria:**
- [ ] All 8 tables from §5 exist with correct foreign keys.
- [ ] App startup creates tables without error on a fresh database.
- [ ] `Report`/`Flag` schemas match the extended shape described in `SYSTEM_DESIGN.md` §5.

**Maps to:** supports FR-4, FR-27, FR-29, FR-30

**Notes / risks:** SQLite by default is fine for the hackathon even though `SYSTEM_DESIGN.md` names Postgres — swapping `DATABASE_URL` later is a config change, not a code change; no Alembic setup time needed.

---

### TKT-003 — Object storage helper service
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-001 |
| Demo value | None standalone — unblocks the upload ticket. |

**User / system outcome:** the backend can store and retrieve uploaded files without ever exposing a raw bucket URL to the client.

**Scope:**
- `services/storage.py`: `upload_file(bytes, key)`, `get_signed_url(key)` using `boto3` against an S3-compatible endpoint, reading credentials from `settings`.

**Out of scope:**
- Provisioning the actual bucket (documented as a setup step in README, TKT-042).

**Acceptance criteria:**
- [ ] Can upload bytes and get back a `storage_key`.
- [ ] Can generate a short-lived signed URL for a given key.
- [ ] No raw bucket URL or credentials are ever returned to the caller.

**Notes / risks:** if no real S3-compatible bucket is available mid-hackathon, a local-disk fallback behind the same function signatures is acceptable — leave a `# TODO` rather than blocking the demo on cloud storage setup.

---

### TKT-004 — Auth backend: signup + login (JWT)
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-002 |
| Demo value | Signup + login work via Swagger/`curl`, returning a usable JWT. |

**User / system outcome:** a user can create an account and log in, per FR-1/FR-2.

**Scope:**
- `routes/auth.py` *(new)*: `POST /api/auth/signup`, `POST /api/auth/login`.
- `passlib` bcrypt password hashing.
- `pyjwt` access-token issuance (~15 min).

**Out of scope:**
- Refresh/logout (TKT-005), password reset (TKT-012).

**Acceptance criteria:**
- [ ] `POST /api/auth/signup` creates a user with a hashed password and rejects a duplicate email.
- [ ] `POST /api/auth/login` returns an access token for correct credentials and 401s for incorrect ones.
- [ ] Password is never returned or logged in plaintext.

**Maps to:** FR-1, FR-2

---

### TKT-005 — Auth backend: refresh + logout
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | backend |
| Priority | P1 |
| Depends on | TKT-004 |
| Demo value | Session survives a simulated reload without re-login; logout actually ends the session. |

**User / system outcome:** FR-2's "persists across reloads" and FR-3 (logout) are real, not just a long-lived access token.

**Scope:**
- Use the `refresh_tokens` table (hashed token storage).
- `POST /api/auth/refresh` (rotate access token), `POST /api/auth/logout` (revoke refresh token).

**Out of scope:**
- Multi-device session management/listing.

**Acceptance criteria:**
- [ ] A refresh token is issued at login and stored hashed.
- [ ] `POST /api/auth/refresh` returns a new access token given a valid refresh token.
- [ ] `POST /api/auth/logout` revokes the refresh token; a subsequent refresh attempt fails.

**Maps to:** FR-2, FR-3

---

### TKT-006 — Auth frontend: login/signup pages
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-004 |
| Demo value | A user can sign up / log in through the browser and land on the dashboard. |

**Scope:**
- `app/login/page.tsx`, `app/signup/page.tsx` (client components, controlled inputs + `useState`).
- `lib/api.ts` fetch wrapper, `lib/types.ts` (`User`, auth response types).
- Token storage (e.g. `localStorage`) and redirect to `/dashboard` on success.

**Out of scope:**
- Password reset UI.

**Acceptance criteria:**
- [ ] User can sign up via the UI and lands on the dashboard.
- [ ] User can log in via the UI and lands on the dashboard.
- [ ] Invalid credentials show an inline error, not a crash.
- [ ] The session persists across a page reload without re-authenticating.

**Maps to:** FR-1, FR-2

---

### TKT-007 — Upload backend: `POST /api/upload`
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-002, TKT-003 |
| Demo value | Swagger upload of a real PDF/DOCX returns a `document_id`. |

**Scope:**
- Real `routes/upload.py`: multipart file + `doc_type`, validate type (`pdf`/`docx`) and size limit, call `storage.py`, create a `documents` row (`status=uploaded`), return `document_id`. JWT-authenticated, scoped to `user_id`.

**Out of scope:**
- Triggering analysis (that's `POST /api/analyze/{document_id}`, TKT-016).

**Acceptance criteria:**
- [ ] A valid PDF/DOCX + `doc_type` creates a `documents` row and returns a `document_id`.
- [ ] An oversized or unsupported file type is rejected with a clear 4xx + `detail` message.
- [ ] An unauthenticated request is rejected with 401.
- [ ] The created row's `user_id` matches the authenticated user.

**Maps to:** FR-6, FR-7, FR-8, FR-9

---

### TKT-008 — Documents backend: list + status endpoints
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-002 |
| Demo value | The dashboard and status page have real data to render. |

**Scope:**
- `GET /api/documents` (current user's documents).
- `GET /api/documents/{id}` (status/progress; 404 if not owned by requester).

**Out of scope:**
- `DELETE /api/documents/{id}` (Phase 5, TKT-037).

**Acceptance criteria:**
- [ ] `GET /api/documents` returns only the requesting user's documents.
- [ ] `GET /api/documents/{id}` returns 404 (not 403) for another user's document id.
- [ ] Response includes `status` and a `risk_score` placeholder field for later phases.

**Maps to:** FR-27, FR-30

---

### TKT-009 — Upload frontend: `/upload` page
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-007, TKT-006 |
| Demo value | A user can pick a doc type, drag a file in, and see upload confirmation. |

**Scope:**
- `app/upload/page.tsx`: doc-type select (rental/employment), drag-and-drop file input, calls `apiFetch` → `POST /api/upload`, success state showing confirmation + `document_id`, link forward to the status page.

**Out of scope:**
- Wiring the actual "start analysis" call (Phase 2, TKT-019) — a disabled/placeholder button or direct link to the status page is fine here.

**Acceptance criteria:**
- [ ] User selects a doc type + file and submits successfully.
- [ ] Success state is shown before any analysis starts (per FR-9).
- [ ] An unsupported file/type shows the backend's error message inline.

**Maps to:** FR-6, FR-7, FR-9

---

### TKT-010 — Dashboard frontend: document list shell
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-008, TKT-006 |
| Demo value | Landing page after login shows the user's documents. |

**Scope:**
- `app/dashboard/page.tsx`: server component fetching `GET /api/documents`; list with filename/status/doc_type; risk badge placeholder ("—") until Phase 2/3; links to `/documents/[id]` or `/reports/[id]`; entry point to `/upload`.

**Out of scope:**
- Real risk badge values (Phase 2/3), delete button (Phase 5).

**Acceptance criteria:**
- [ ] Dashboard lists only the current user's documents.
- [ ] An empty state is shown when there are no documents.
- [ ] Each row links to the correct status or report page.

**Maps to:** FR-27

---

### TKT-011 — Document status page shell (`/documents/[id]`)
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | frontend |
| Priority | P1 |
| Depends on | TKT-008 |
| Demo value | A dedicated page exists to show a document's status (stub before real analysis exists). |

**Scope:**
- `app/documents/[id]/page.tsx`: shows the current `status` field fetched from `GET /api/documents/{id}`. Before Phase 2, this statically shows "uploaded" — a real polling loop is added in TKT-019.

**Out of scope:**
- Real stage progression UI (extracting → analyzing → grounding) — Phase 2, TKT-019.

**Acceptance criteria:**
- [ ] Page renders for a valid document id owned by the user.
- [ ] Page 404s/redirects for a document not owned by the user.

**Maps to:** FR-11 (partial/stub)

---

### TKT-012 — [Decision] Password reset scope for MVP (OQ-6)
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | docs |
| Priority | P2 |
| Depends on | none |
| Demo value | None — non-implementation ticket, prevents silently over- or under-building FR-5. |

**User / system outcome:** an explicit, recorded decision instead of an assumption.

**Scope:**
- Record the decision below.

**Decision:** Password reset (FR-5, priority COULD) is **deferred** for MVP. Revisit only if judging criteria specifically call it out.

**Out of scope:**
- Implementing password reset.

**Acceptance criteria:**
- [x] Decision recorded above.

---

### TKT-013 — Phase 1 demo checkpoint
| Field | Value |
|---|---|
| Phase | 1 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-001…TKT-011 |
| Demo value | Full click-through: signup → login → upload → dashboard. |

**User / system outcome:** the Phase 1 product outcome from `PRD.md` §11 is real and demoable.

**Scope:**
- Manual E2E smoke test across all Phase 1 tickets; fix any integration gaps (CORS, token propagation, dashboard refresh after upload).

**Out of scope:**
- Anything from Phase 2+.

**Acceptance criteria:**
- [ ] A new user can sign up, log in, upload a document, and see it listed on the dashboard with status "uploaded" in one sitting, with no console errors.
- [ ] A second user cannot see the first user's document anywhere in the UI or via direct API calls.

**Notes / risks:** treat this as a hard gate — don't start Phase 2 tickets if this fails.

### Phase 2 — Core analysis

### TKT-014 — Text extraction service
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-002 |
| Demo value | None standalone — unblocks the analysis pipeline. |

**Scope:**
- `services/extraction.py`: `pdfplumber` for PDFs, `python-docx` for DOCX; a text-density heuristic that triggers page-image rendering + a Gemini multimodal call for scanned/low-text pages.

**Out of scope:**
- Clause segmentation (TKT-015).

**Acceptance criteria:**
- [ ] A digital PDF/DOCX returns extracted text.
- [ ] A simulated scanned/low-text PDF triggers the Gemini multimodal fallback path (a mocked/test case is acceptable if no real scanned sample is on hand).

**Maps to:** FR-12

---

### TKT-015 — Gemini analysis service
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-014 |
| Demo value | None standalone — core analysis logic used by the pipeline. |

**Scope:**
- `services/llm.py`: clause segmentation (fixed taxonomy per `doc_type`), risk analysis pass (plain-language issue + severity per clause), missing-clause checklist diff using the rental/employment checklists from `SYSTEM_DESIGN.md` §4 step 5.

**Out of scope:**
- Grounding/citations (Phase 3), voice Q&A answering (Phase 4 — added as a separate function later, TKT-030).

**Acceptance criteria:**
- [ ] Given extracted text + `doc_type=rental`, returns typed clauses, flags with plain-language issue + severity, and a missing-clause list from the rental checklist.
- [ ] Given `doc_type=employment`, non-compete/notice-pay/termination clauses are evaluated using the employment checklist.
- [ ] Uses `GEMINI_API_KEY` from `settings`, never hardcoded.

**Maps to:** FR-13, FR-14, FR-15

---

### TKT-016 — Analyze pipeline orchestration
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-015, TKT-008 |
| Demo value | Triggering analysis actually processes a document end to end. |

**Scope:**
- Real `routes/analyze.py`: `POST /api/analyze/{document_id}` kicks off a FastAPI `BackgroundTasks` job: `status=processing` → extract → segment/analyze → missing-clause diff → `status=analyzed`, updating `documents.status` at each stage for polling.

**Out of scope:**
- The Exa grounding step (added in TKT-024), voice.

**Acceptance criteria:**
- [ ] Triggering analyze moves the document out of "uploaded" and eventually to "analyzed".
- [ ] The endpoint returns immediately; it is not blocked on pipeline completion.
- [ ] A scanned/low-text document still completes via the multimodal fallback, not a failure.

**Maps to:** FR-10, FR-11 (stage field)

---

### TKT-017 — Report persistence + `GET /api/reports/{id}`
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-016 |
| Demo value | A completed analysis produces a fetchable report. |

**Scope:**
- `routes/reports.py` *(new)*: persist `Report`/`Flag`/`MissingClause`/`ActionItem` rows at the end of the pipeline; `GET /api/reports/{id}` scoped to the owner, with an aggregated `risk_score`.

**Out of scope:**
- Citations (Phase 3).

**Acceptance criteria:**
- [ ] After analyze completes, `GET /api/reports/{id}` returns `risk_score`, `flags`, `missing_clauses`, and `action_items`.
- [ ] A request for another user's report returns 404.
- [ ] `risk_score` is one of green/yellow/red only.

**Maps to:** FR-16, FR-17 (partial — no citations yet), FR-20, FR-21, FR-28

---

### TKT-018 — [Spike] Latency/SLA expectations (OQ-5)
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | docs |
| Priority | P2 |
| Depends on | TKT-016 |
| Demo value | None — informs whether progress messaging (TKT-019) needs adjustment. |

**Scope:**
- Time a real analyze run end to end for a representative rental and employment document; record observed latency.

**Acceptance criteria:**
- [ ] Observed latency recorded in this document for at least one sample document per `doc_type`.

**Notes / risks:** does not block Phase 2's demo checkpoint; purely informational.

---

### TKT-019 — Analyze trigger + status polling UI
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-016, TKT-011 |
| Demo value | A judge sees the "extracting → analyzing → grounding" progress live, not a spinner. |

**Scope:**
- Wire `/documents/[id]` to poll `GET /api/documents/{id}` on an interval, render the current stage, redirect to `/reports/[id]` on `analyzed`.
- Add a "Start analysis" action (from `/upload` success or the dashboard) calling `POST /api/analyze/{document_id}`.

**Acceptance criteria:**
- [ ] Clicking "Start analysis" moves the UI through visible stages, not a generic loading spinner.
- [ ] On completion, the user is taken to (or linked to) the report page.

**Maps to:** FR-10, FR-11

---

### TKT-020 — Report page UI
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-017 |
| Demo value | The core report — the product's main value — is visible in the browser. |

**Scope:**
- `app/reports/[id]/page.tsx`: risk badge, flags list (clause, issue, severity — citation UI added in Phase 3), missing clauses with recommendations, action items list.

**Out of scope:**
- Citation badges (Phase 3, TKT-025), audio/voice (Phase 4).

**Acceptance criteria:**
- [ ] Report renders risk badge, all flags, missing clauses, and action items from the API.
- [ ] Loading and error states are handled (not a blank page on failure).

**Maps to:** FR-16, FR-17 (partial), FR-20, FR-21

---

### TKT-021 — Disclaimer component + API field
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-017, TKT-020 |
| Demo value | Every report visibly and provably carries the "not legal advice" notice. |

**Scope:**
- Shared `<Disclaimer />` component rendered prominently on the report page.
- Backend includes a disclaimer string/field on the report API response (not UI-only).

**Acceptance criteria:**
- [ ] Disclaimer text is visible on every report page render, not buried in fine print.
- [ ] `GET /api/reports/{id}` response includes the disclaimer field.

**Maps to:** FR-22

---

### TKT-022 — Phase 2 demo checkpoint
| Field | Value |
|---|---|
| Phase | 2 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-014…TKT-021 |
| Demo value | Full click-through: upload → analyze → report (no citations yet). |

**Acceptance criteria:**
- [ ] Upload → analyze → report works end to end for both `rental` and `employment` doc types, with visible stage progress and a disclaimer.

### Phase 3 — Grounding

### TKT-023 — Exa grounding service
| Field | Value |
|---|---|
| Phase | 3 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-015 |
| Demo value | None standalone — core anti-hallucination logic. |

**Scope:**
- `services/grounding.py`: per-flag/missing-clause targeted query generation, Exa search + contents call, trusted-domain filter (`indiacode.nic.in`, `indiankanoon.org`, government/ministry sources), citation extraction (title, url, snippet). Returns `verified=false` when no source clears the confidence bar.

**Acceptance criteria:**
- [ ] Given a flag description, returns either a real citation from a trusted domain or `verified=false` with no fabricated citation.
- [ ] Results from non-trusted domains are filtered out.

**Maps to:** FR-18, FR-19

---

### TKT-024 — Wire grounding into pipeline + persist citations
| Field | Value |
|---|---|
| Phase | 3 |
| Surface | backend |
| Priority | P0 |
| Depends on | TKT-023, TKT-016 |
| Demo value | Reports now carry real (or explicitly unverified) citations. |

**Scope:**
- Call `grounding.py` for each flag/missing clause during the analyze pipeline; persist `Citation` rows (with `verified` boolean) linked to each flag.

**Acceptance criteria:**
- [ ] After analyze, flags in the DB have zero or more citations, each with a `verified` boolean.
- [ ] A flag with no reliable source found is explicitly marked unverified, never given a fabricated citation.

**Maps to:** FR-18, FR-19

---

### TKT-025 — Citation UI: verified/unverified badges
| Field | Value |
|---|---|
| Phase | 3 |
| Surface | frontend |
| Priority | P0 |
| Depends on | TKT-020, TKT-024 |
| Demo value | The anti-hallucination guarantee is visible to a judge, not just present in the data. |

**Scope:**
- Extend the report page's flag/missing-clause rendering with a visible badge/label distinguishing **verified** (real source, linked) vs **unverified** ("unverified / general principle").

**Acceptance criteria:**
- [ ] Every flag/missing-clause with a citation visibly shows verified or unverified — never ambiguous.
- [ ] Verified citations link out to the source URL.

**Maps to:** FR-17, PRD §10 product requirement (verified distinction must be visually distinguishable)

---

### TKT-026 — Phase 3 demo checkpoint
| Field | Value |
|---|---|
| Phase | 3 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-023…TKT-025 |
| Demo value | The product's core differentiator (grounded, not-hallucinated citations) is demoable. |

**Acceptance criteria:**
- [ ] A judge can see at least one verified citation with a working source link and at least one unverified label in a demo report.

### Phase 4 — Voice

### TKT-027 — [Spike] Wispr Flow server-callable STT feasibility (OQ-1)
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | docs |
| Priority | P0 (blocker) |
| Depends on | none |
| Demo value | None — unblocks/redirects TKT-029, TKT-032. |

**Scope:**
- Research whether Wispr Flow exposes a server-callable STT API (vs. desktop-only dictation). Record the finding and the go/no-go decision for downstream tickets.

**Acceptance criteria:**
- [ ] Decision recorded: either "Wispr Flow is usable server-side" or "fallback to browser Web Speech API is required."

**Notes / risks:** `SYSTEM_DESIGN.md` §11 already flags this as unconfirmed. TKT-029/030/032 branch on this outcome — do not start them until this is resolved.

---

### TKT-028 — TTS backend: ElevenLabs `speak` endpoint
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | backend |
| Priority | P1 |
| Depends on | TKT-017 |
| Demo value | A report summary can be converted to audio via the API. |

**Scope:**
- `services/voice.py` (TTS half) + real `routes/voice.py`: `POST /api/voice/speak` — text in (report summary), audio out via ElevenLabs.

**Acceptance criteria:**
- [ ] `POST /api/voice/speak` with a report summary returns playable audio.
- [ ] `ELEVENLABS_API_KEY` is read from `settings`, never exposed to the client.

**Maps to:** FR-23

---

### TKT-029 — STT backend: `transcribe` endpoint
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | backend |
| Priority | P1 |
| Depends on | TKT-027 |
| Demo value | Depends on TKT-027's finding — either real Wispr transcription or an explicit "use the frontend fallback" contract. |

**Scope:**
- `services/voice.py` (STT half) + `POST /api/voice/transcribe` — backed by Wispr Flow if TKT-027 found it usable; otherwise this ticket documents the endpoint as unsupported server-side, with the fallback moving entirely client-side (TKT-032).

**Acceptance criteria:**
- [ ] If Wispr is usable: audio in → transcript out via Wispr Flow.
- [ ] If not usable: the endpoint/contract explicitly documents itself as unsupported, and the frontend fallback (TKT-032) is the primary path — no silent failure.

**Maps to:** FR-24, FR-26

---

### TKT-030 — Voice Q&A backend: Gemini grounded answer
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | backend |
| Priority | P1 |
| Depends on | TKT-024, TKT-015 |
| Demo value | A follow-up question gets an answer grounded only in the existing report. |

**Scope:**
- `llm.py` addition: `answer_question(document_context, report, citations, question)`, constrained to only the analyzed document + existing report/citations, introducing no new claims.

**Acceptance criteria:**
- [ ] Given a question outside the report's scope, the answer explicitly declines to introduce new legal claims rather than inventing one.
- [ ] The answer references only citations already present in the report.

**Maps to:** FR-25

---

### TKT-031 — Audio summary playback UI
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | frontend |
| Priority | P1 |
| Depends on | TKT-028, TKT-020 |
| Demo value | "Listen to summary" works from the report page. |

**Scope:**
- Add a "Listen to summary" button/player on the report page calling `POST /api/voice/speak`.

**Acceptance criteria:**
- [ ] User can play/pause an audio summary of the report from the report page.

**Maps to:** FR-23

---

### TKT-032 — Voice Q&A UX (mic + Web Speech fallback)
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | frontend |
| Priority | P1 |
| Depends on | TKT-029, TKT-030 |
| Demo value | A judge can ask a spoken question and get a spoken/text answer, regardless of Wispr availability. |

**Scope:**
- Mic button on the report page. If TKT-027 found Wispr unusable, use the browser Web Speech API client-side to capture the question instead of calling `/api/voice/transcribe`; send the transcript to the Q&A path from TKT-030 and display the grounded answer (optionally replayed via TKT-028).

**Acceptance criteria:**
- [ ] User can ask a question by voice (via the Wispr-backed endpoint or the Web Speech fallback) and see/hear a grounded answer.
- [ ] If the primary STT provider is unavailable, the fallback path still lets the user submit a spoken question.

**Maps to:** FR-24, FR-26

---

### TKT-033 — Phase 4 demo checkpoint (optional)
| Field | Value |
|---|---|
| Phase | 4 |
| Surface | fullstack |
| Priority | P1 |
| Depends on | TKT-028…TKT-032 |
| Demo value | Voice in/out is demoable, on whichever STT path TKT-027 resolved to. |

**Acceptance criteria:**
- [ ] A judge can listen to a report summary and ask one spoken question, getting a grounded answer.

**Notes / risks:** this entire phase is P1/optional for the main demo path — if `TKT-027` resolves unfavorably late, the fallback-only path (Web Speech + text answer) still satisfies FR-24/FR-26 without a working Wispr integration.

### Phase 5 — Deployment & hardening

### TKT-034 — Render deployment
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | infra |
| Priority | P0 |
| Depends on | TKT-022 |
| Demo value | The product is reachable at a real URL for judges. |

**Scope:**
- Deploy backend (`uvicorn`) + frontend (`next build`/`next start`) as separate Render web services; provision managed Postgres; set env var groups (all API keys, `JWT_SECRET`, `DATABASE_URL`, S3 credentials); point `NEXT_PUBLIC_API_URL` at the deployed backend; update CORS to include the deployed frontend URL.

**Acceptance criteria:**
- [ ] The deployed frontend URL can complete the Phase 1–3 flow against the deployed backend.
- [ ] `/health` returns 200 on the deployed backend.

**Notes / risks:** if Phase 4 isn't ready by deployment time, deploy without it — voice is additive per `ARCHITECTURE.md` and doesn't block the core path.

---

### TKT-035 — [Decision] Rate-limit thresholds (OQ-3)
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | docs |
| Priority | P1 |
| Depends on | none |
| Demo value | None — unblocks TKT-036. |

**Scope:**
- Record a placeholder default so implementation isn't blocked on a perfect number.

**Decision (placeholder, adjustable):** 20 uploads/user/hour, 10 analyze triggers/user/hour. Not a final SLA commitment — revisit if real usage data emerges.

**Acceptance criteria:**
- [x] Placeholder thresholds recorded above for TKT-036 to implement.

---

### TKT-036 — Rate limiting middleware on upload/analyze
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | backend |
| Priority | P1 |
| Depends on | TKT-035 |
| Demo value | Cost/abuse exposure is bounded before judging/demo traffic hits the deployed instance. |

**Scope:**
- Per-user rate limit (in-memory or simple DB-backed counter — no Redis) on `POST /api/upload` and `POST /api/analyze/{document_id}` using TKT-035's thresholds.

**Acceptance criteria:**
- [ ] Exceeding the threshold returns a clear 429 with a user-facing message, not a raw exception.

---

### TKT-037 — Delete flow
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-008, TKT-010 |
| Demo value | A judge can delete a document live and see it's fully gone. |

**Scope:**
- `DELETE /api/documents/{id}` — cascades to the blob (`storage.py`), document row, report, flags, citations, missing_clauses, action_items.
- Dashboard delete button + confirmation.

**Acceptance criteria:**
- [ ] Deleting a document removes it from the dashboard immediately.
- [ ] A subsequent `GET /api/documents/{id}` or `GET /api/reports/{id}` returns 404 after delete.
- [ ] The underlying blob is removed from object storage.

**Maps to:** FR-29

---

### TKT-038 — [Decision] Minimal delete needed earlier than Phase 5?
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | docs |
| Priority | P1 |
| Depends on | none |
| Demo value | None — records a scope decision so it isn't silently revisited. |

**Decision:** delete stays **Phase 5-only**, per `PRD.md` §11 phasing. No early Phase 1 delete button.

**Acceptance criteria:**
- [x] Decision recorded above.

---

### TKT-039 — Monitoring/health hardening
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | infra |
| Priority | P1 |
| Depends on | TKT-034 |
| Demo value | Pipeline failures are debuggable without exposing internals to users. |

**Scope:**
- Structured logging (`INFO` level) for request-relevant events (upload created, analyze failed, external API call failed).
- `/health` reflects DB connectivity, not just a static 200.

**Acceptance criteria:**
- [ ] Key pipeline failures are logged server-side with enough context to debug, without leaking secrets.
- [ ] `/health` fails loudly (non-200) if the DB is unreachable.

---

### TKT-040 — [Spike] Accessibility conformance target (OQ-4)
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | docs |
| Priority | P2 |
| Depends on | none |
| Demo value | None — decision only. |

**Decision:** no formal WCAG conformance target for MVP beyond the voice input/output already built in Phase 4. Revisit if a judge or user explicitly raises it.

**Acceptance criteria:**
- [x] Decision recorded above.

---

### TKT-041 — [Decision] Project naming: Lexo vs VectorMinds (OQ-2)
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | docs |
| Priority | P2 |
| Depends on | none |
| Demo value | Consistent branding across README and product docs. |

**Scope:**
- Decide the canonical name; if "Lexo," update the root `README.md` title (currently "VectorMinds") to match.

**Acceptance criteria:**
- [ ] Decision recorded and root `README.md` title matches it.

---

### TKT-042 — README polish + `.env.example` final audit
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | docs |
| Priority | P0 |
| Depends on | TKT-034 |
| Demo value | Anyone (a judge, a teammate) can run the project from the README alone. |

**Scope:**
- Root/`lexo` README: what it does, how to run backend + frontend locally, the deployed link.
- Confirm `backend/.env.example` and `frontend/.env.local.example` match every var actually read by `settings`/`process.env`.

**Acceptance criteria:**
- [ ] A new teammate can run backend + frontend from the README alone.
- [ ] Every var read in code is present in the matching `.env.example`, and vice versa.

---

### TKT-043 — Disclaimer audit across all report surfaces
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | fullstack |
| Priority | P1 |
| Depends on | TKT-021, TKT-025 |
| Demo value | The "not legal advice" guarantee holds everywhere, not just the happy path. |

**Scope:**
- Confirm the disclaimer appears on the report page, on any voice-adjacent surfaces, and on every relevant API response, per `PRD.md` §8/§22.

**Acceptance criteria:**
- [ ] Disclaimer present on 100% of report-viewing surfaces (UI + API), verified by a manual pass.

---

### TKT-044 — Phase 5 demo checkpoint
| Field | Value |
|---|---|
| Phase | 5 |
| Surface | fullstack |
| Priority | P0 |
| Depends on | TKT-034…TKT-043 |
| Demo value | The full product story, live, on a real URL. |

**Acceptance criteria:**
- [ ] Full flow (signup → upload → analyze → grounded report → optional voice → delete) works on the deployed Render URL, with rate limiting active and no exposed secrets/stack traces.

## 7. Spikes / Open Questions

| ID | Open question | Ticket | Blocks |
|---|---|---|---|
| OQ-1 | Does Wispr Flow expose a server-callable STT API? | TKT-027 | Phase 4 |
| OQ-2 | Is "Lexo" or "VectorMinds" the canonical name? | TKT-041 | Branding only, not a build blocker |
| OQ-3 | Concrete rate-limit thresholds for upload/analyze? | TKT-035 | Phase 5 |
| OQ-4 | Target accessibility conformance level? | TKT-040 | Phase 5 / ongoing |
| OQ-5 | Latency/SLA targets for analysis? | TKT-018 | Phase 2 validation |
| OQ-6 | Is password reset (FR-5) required for MVP? | TKT-012 | Phase 1 scope |

None of these are resolved by inventing an answer in a ticket — each spike/decision ticket above either records a real finding or an explicit, reversible scope call.

## 8. Explicitly Deferred / Won't Do for MVP

Pulled from `PRD.md` §4 (Non-Goals) and §15 (Out of Scope). No ticket in this backlog should build any of the following:

- Document types other than rental and employment agreements.
- Jurisdictions other than India.
- Acting as, or being positioned as, a substitute for a licensed lawyer; any feature giving a definitive legal conclusion rather than a flagged-for-review, plain-language analysis.
- Real-time legal advice or negotiation support (e.g. redlining, contract negotiation on the user's behalf).
- Multi-party / collaborative review (sharing a report with a landlord, HR, or counterparty for negotiation).
- Guaranteeing a citation exists for every flag — when no reliable source is found, the correct behavior is labeling it unverified, not searching indefinitely or guessing.
- Languages beyond what the current text-extraction/LLM pipeline supports natively.
- Graduating the async pipeline from FastAPI `BackgroundTasks` to a dedicated queue (Celery + Redis, or a Render Background Worker) — not required unless load demands it.
