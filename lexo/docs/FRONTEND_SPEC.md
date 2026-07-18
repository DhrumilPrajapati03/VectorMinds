# Lexo — Frontend Spec

## 1. Document Control

| Field | Value |
|---|---|
| Status | **Draft** |
| Product | Lexo — AI legal-document assistant (rental & employment agreements, India) |
| Related docs | [`PRD.md`](./PRD.md) (product requirements, personas, acceptance criteria), [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) (architecture, data model, API contract, pipeline), [`ARCHITECTURE.md`](./ARCHITECTURE.md) (high-level onboarding overview) |
| Scope of this doc | Frontend implementation handoff only: routes, screen states, components, client-side API usage, auth/session UX, polling, voice UX, empty/error states, MVP vs later UI. It does **not** restate product rationale (see `PRD.md`) or backend pipeline/data-model detail (see `SYSTEM_DESIGN.md`) — it links to those instead of duplicating them. |

This doc assumes the reader has skimmed `PRD.md` §6 (journeys) and `SYSTEM_DESIGN.md` §3.1 and §6 (frontend area + API contract).

## 2. Goals of the Frontend

- Let a user sign up, log in, and stay logged in across reloads without friction (PRD §6.1).
- Make uploading a document (type + file) fast and clearly confirm success before analysis starts (PRD §6.2).
- Show real processing progress during analysis, not a silent spinner, so the user trusts the system is working (PRD §6.3).
- Present the report so the single most important trust signal — verified vs. unverified citations — is impossible to miss (PRD §6.4, §10).
- Make voice (listen + ask) a genuinely usable alternative to reading dense text, once enabled (PRD §6.5).
- Give the user an at-a-glance history of their own documents and reports, and a safe, unambiguous way to delete one (PRD §6.6, §6.7).
- Never let one user's session reach another user's data, and never let the UI imply more legal certainty than the backend actually provides (PRD §4, §8).

## 3. Tech Baseline

- **Framework:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS. Matches `lexo/frontend/package.json` today.
- **Structure:** follows the workspace convention — `app/` (one folder per route), `components/` (PascalCase, reusable UI), `lib/api.ts` (fetch wrapper), `lib/types.ts` (types mirroring backend schemas). None of these exist yet beyond `app/page.tsx` and `app/layout.tsx`.
- **Browser-facing env vars:** the frontend needs exactly one env var — `NEXT_PUBLIC_API_URL` (backend base URL, e.g. `http://localhost:8000` in dev). No other value needs to reach the browser.
- **Secrets that must NOT be in frontend env:** `EXA_API_KEY`, `ELEVENLABS_API_KEY`, `WISPR_API_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`/`LLM_API_KEY`, JWT signing secret, object-storage credentials. These are backend-only (`lexo/backend/.env`) per `SYSTEM_DESIGN.md` §8. Any value without a `NEXT_PUBLIC_` prefix is invisible to the browser by design — server secrets belong only in the backend's env, never in `lexo/frontend/.env.local`.
- **Follow-up flagged, not fixed here (no app code changes in this doc's scope):** [`lexo/frontend/.env.local.example`](../frontend/.env.local.example) currently contains an exact copy of the backend's `.env.example` (`EXA_API_KEY`, `ELEVENLABS_API_KEY`, `WISPR_API_KEY`, `DATABASE_URL`, `LLM_API_KEY`) and is **missing `NEXT_PUBLIC_API_URL` entirely**. This is incorrect for a frontend env file and should be corrected in a future implementation pass (delete the backend-only keys, add `NEXT_PUBLIC_API_URL=`).

## 4. Information Architecture & Routes

| Path | Auth required | Purpose | Primary API calls |
|---|---|---|---|
| `/login` | No (redirect away if already authenticated) | Existing user signs in | `POST /api/auth/login` |
| `/signup` | No (redirect away if already authenticated) | New user creates an account | `POST /api/auth/signup` |
| `/dashboard` | Yes | Lists the user's documents/reports with status + risk badge; entry point to upload | `GET /api/documents`, `DELETE /api/documents/{id}` |
| `/upload` | Yes | Select `doc_type`, choose/drag-and-drop a file, submit | `POST /api/upload`, `POST /api/analyze/{document_id}` |
| `/documents/[id]` | Yes | Shows processing status while a document is being analyzed | `GET /api/documents/{id}` (polled) |
| `/reports/[id]` | Yes | Full report: risk badge, flags/citations, missing clauses, action items, disclaimer, voice entry points | `GET /api/reports/{id}`, `POST /api/voice/speak`, `POST /api/voice/ask` (text); STT is client-side Web Speech — do not call `/api/voice/transcribe` |

No routes or endpoints beyond this table are assumed anywhere in this doc.

## 5. Global UX

- **Layout/nav:** a minimal top bar (Lexo wordmark, link to `/dashboard`, logout control) present on all authenticated routes. Auth routes (`/login`, `/signup`) render standalone without the app nav.
- **Auth gate:** a single client-side check (e.g. an `AuthGate`/`useAuth` hook wrapping protected routes) reads the stored access token. If missing/expired on a protected route, redirect to `/login`. If present on `/login` or `/signup`, redirect to `/dashboard`. On any `401` response from the API, clear the stored session and redirect to `/login`.
- **Loading pattern:** every data-fetching component/screen shows an explicit loading state (skeleton or spinner + label) — never a blank screen. Route-level data fetching prefers Server Components per the workspace Next.js rule; interactive/auth-dependent screens that need client-side tokens use `"use client"` only where required.
- **Error pattern:** two consistent conventions, used consistently rather than per-endpoint custom parsing:
  - **Inline field errors** (e.g. bad login credentials, invalid upload file) — shown next to the form/control that caused them, sourced from the backend's standard `{"detail": "..."}` shape.
  - **Toast/banner errors** (e.g. failed to load dashboard list, failed to delete) — shown as a dismissible banner at the top of the affected screen, not a blocking modal.
- **Disclaimer placement rule:** the "this is not legal advice" notice is visible on every render of `/reports/[id]` (success state), positioned near the top of the report (above or beside the risk badge), not buried in a footer — per PRD §10's requirement that this be a UX concern, not just a data field.

## 6. Screen Specs

### 6.1 `/login`

**Purpose:** existing user signs in and lands on `/dashboard`.

**Layout:** centered single-column form — email field, password field, submit button, link to `/signup`.

**User actions:** submit email + password.

**API calls:** `POST /api/auth/login`.

**States:**
| State | Behavior |
|---|---|
| Empty | Form with empty fields, submit disabled until both fields are non-empty |
| Loading | Submit button shows a busy state; fields disabled during request |
| Success | Store access (+ refresh) token; redirect to `/dashboard` |
| Error | Incorrect credentials → inline error under the form (from `{"detail": "..."}`); fields remain filled |
| Edge | Already-authenticated user navigates to `/login` directly → immediate redirect to `/dashboard` before rendering the form |

**Acceptance criteria:**
- [ ] User can log in with correct credentials and is redirected to `/dashboard` (PRD Acceptance Criteria — Auth).
- [ ] User cannot log in with incorrect credentials; a clear inline error is shown (PRD Acceptance Criteria — Auth).
- [ ] A logged-in user's session persists across a page reload without re-authentication (PRD Acceptance Criteria — Auth).

### 6.2 `/signup`

**Purpose:** new user creates an account and lands on `/dashboard`.

**Layout:** centered single-column form — email, password (and confirm-password, client-side only), submit button, link to `/login`.

**User actions:** submit email + password to create an account.

**API calls:** `POST /api/auth/signup`.

**States:**
| State | Behavior |
|---|---|
| Empty | Form with empty fields, submit disabled until required fields are filled and passwords match |
| Loading | Submit button busy state; fields disabled |
| Success | Store access (+ refresh) token; redirect to `/dashboard` |
| Error | Email already registered → inline error under the email field; other validation errors (e.g. weak password, if backend enforces) shown the same way |
| Edge | Already-authenticated user navigates to `/signup` directly → immediate redirect to `/dashboard` |

**Acceptance criteria:**
- [ ] User can sign up with a valid email/password and is redirected to `/dashboard` (PRD Acceptance Criteria — Auth).
- [ ] User cannot sign up twice with the same email; a clear inline error is shown (PRD Acceptance Criteria — Auth).

### 6.3 `/dashboard`

**Purpose:** entry point after login; lists the user's own documents/reports with status and risk badge, and links to start a new upload.

**Layout:** a page header with an "Upload new document" action, followed by a list of the user's documents. Each row/card shows: filename, `doc_type`, status, risk badge (once analyzed), created date, and a delete control. No card-spam grid needed — a simple list is sufficient.

**User actions:** navigate to `/upload`; open a document (→ `/documents/[id]` if still processing, or `/reports/[id]` if analyzed); delete a document (with a confirmation step, since deletion cascades and is irreversible per PRD §6.7).

**API calls:** `GET /api/documents` on mount; `DELETE /api/documents/{id}` on delete confirmation.

**States:**
| State | Behavior |
|---|---|
| Empty | No documents yet → friendly empty state with a prominent "Upload your first document" call to action |
| Loading | List skeleton while `GET /api/documents` is in flight |
| Success | List renders, sorted by most recent first |
| Error | List fetch fails → banner error with a retry action; page shell (header, upload CTA) still renders |
| Edge | Mixed statuses in the same list (some `uploaded`, some `processing`, some `analyzed`) — each row routes to the correct screen for its current status; delete of a currently-processing document is allowed but shown as unrecoverable via the confirmation copy |

**Acceptance criteria:**
- [ ] Dashboard lists only the current user's documents, each with correct status and risk badge (PRD Acceptance Criteria — History & data control).
- [ ] User can reopen any of their own past reports from this list (PRD Acceptance Criteria — History & data control).
- [ ] User can delete a document from the dashboard and it no longer appears afterward (PRD Acceptance Criteria — History & data control).

### 6.4 `/upload`

**Purpose:** select `doc_type`, provide a file, submit it, and start analysis.

**Layout:** a doc-type selector (`rental` / `employment`), a drag-and-drop file dropzone with a fallback "browse files" button, and a submit action. On success, an inline confirmation with an explicit "Start analysis" action (per PRD §6.2 — upload confirmation is shown before analysis is triggered, not auto-started).

**User actions:** select doc type; drag-drop or browse for a file (`pdf`/`docx`); submit upload; confirm "start analysis".

**API calls:** `POST /api/upload` (multipart file + `doc_type`) → on success, `POST /api/analyze/{document_id}` when the user confirms.

**States:**
| State | Behavior |
|---|---|
| Empty | No file selected yet; submit disabled |
| Loading | Upload in progress → progress indicator on the dropzone; "Start analysis" in progress → busy button state |
| Success | Upload succeeded → show filename + doc id confirmation and the "Start analysis" action; after analysis is triggered, redirect to `/documents/[id]` |
| Error | Unsupported file type or over the size limit → clear inline error naming the problem (exact size limit value is an Open Question, §14); network/server error → inline error with a retry |
| Edge | User navigates away after upload succeeds but before triggering analysis — document exists in `/dashboard` with status `uploaded` and can be resumed from there (analysis can be triggered again from the document's own screen, not only from `/upload`) |

**Acceptance criteria:**
- [ ] User can upload a valid PDF or DOCX and receive a document id (PRD Acceptance Criteria — Upload).
- [ ] Selecting "rental" or "employment" is preserved and reflected in the created document (PRD Acceptance Criteria — Upload).
- [ ] Uploading an unsupported type or oversized file is rejected with a clear, user-visible error (PRD Acceptance Criteria — Upload; FR-8).
- [ ] User sees confirmation that the upload succeeded before analysis starts (FR-9).

### 6.5 `/documents/[id]`

**Purpose:** shows live processing progress for a document that has started analysis but isn't complete yet.

**Layout:** a stepper/progress indicator showing the pipeline stages (e.g. extracting → analyzing → grounding, per `SYSTEM_DESIGN.md` §4), the document's filename/doc type for context, and an explanatory line that analysis can take a few minutes.

**User actions:** wait (passive); once status is `analyzed`, follow an automatic or one-click navigation to `/reports/[id]`.

**API calls:** `GET /api/documents/{id}`, polled at a fixed interval while status is `uploaded` or `processing`; polling stops once status is `analyzed` (or a terminal failure state, if the backend exposes one).

**States:**
| State | Behavior |
|---|---|
| Empty | N/A (screen only makes sense once a document exists) |
| Loading | Initial fetch of the document before the first status is known → generic loading skeleton |
| Success (in progress) | Stepper shows the current stage highlighted; earlier stages marked complete |
| Success (complete) | Status is `analyzed` → auto-redirect (or show a clear "View report" button) to `/reports/[id]` |
| Error | Document not found or not owned by the user → treated like a 404, not a leaked-existence message (per FR-4/FR-30); polling request failure → inline retry, keep last known stage visible rather than resetting the stepper |
| Edge | Analysis takes unusually long — no hard timeout is prescribed here; if the backend later exposes a failure status, this screen should render a distinct "analysis failed" state with a retry action (exact failure-state contract is not yet defined — see §14 Open Questions) |

**Acceptance criteria:**
- [ ] User can see the current processing stage while analysis is in progress, not just a generic spinner (FR-11).
- [ ] Triggering analysis moves the document out of "uploaded" status and eventually to a completed state visible on this screen (PRD Acceptance Criteria — Analysis).
- [ ] A logged-in user cannot view another user's document by guessing/changing the `id` in the URL (PRD Acceptance Criteria — Auth).

### 6.6 `/reports/[id]`

**Purpose:** the full report view — risk badge, flags with citations, missing clauses, action items, disclaimer, and voice entry points.

**Layout:** see §7 (Report UI Detail) for the full structure. At a high level: risk badge + summary near the top with the disclaimer, followed by the flags list, missing clauses list, and action items list, with voice controls (listen + ask) placed near the top of the report content.

**User actions:** read the report; expand/inspect individual flags and citations; play the audio summary; ask a spoken question (voice controls — see §8 for MVP-phasing gating); navigate back to `/dashboard`.

**API calls:** `GET /api/reports/{id}` on mount; `POST /api/voice/speak` on "Listen to summary"; `POST /api/voice/ask` with the **text** question (from Web Speech transcript or typed input). Do not call `/api/voice/transcribe`.

**States:**
| State | Behavior |
|---|---|
| Empty | N/A — a report only renders once it exists; if analysis isn't complete, the user should not reach this route (linked only from `/documents/[id]` once `analyzed`) |
| Loading | Skeleton for the report layout while `GET /api/reports/{id}` is in flight |
| Success | Full report renders per §7 |
| Error | Report not found or not owned by the requesting user → treated as not-found, no existence leak (FR-4/FR-30); fetch failure → banner error with retry |
| Edge | All citations on a report are unverified (no reliable sources found) — the report still renders normally, with every citation clearly marked "unverified / general principle" rather than the UI implying something failed |

**Acceptance criteria:**
- [ ] Every flag shown has a plain-language explanation, not legal jargon alone (PRD Acceptance Criteria — Report & grounding).
- [ ] Every flag/missing-clause citation is visibly marked verified or unverified — never presented as a real citation when it isn't (PRD Acceptance Criteria — Report & grounding; PRD §10).
- [ ] The report displays an overall risk badge and a "not legal advice" disclaimer (PRD Acceptance Criteria — Report & grounding).
- [ ] User can reopen any of their own past reports and see the same content as originally generated (PRD Acceptance Criteria — History & data control).

## 7. Report UI Detail

- **Risk badge:** a single, prominent badge mapping `risk_score` to green (low concern) / yellow (some concerns) / red (significant concerns), shown at the top of the report next to the disclaimer.
- **Flag list:** each flag shows its clause reference, plain-language issue description, and severity, followed by its citation(s). Flags are the primary content of the report — render as a list, not a dense table.
- **Citation verified/unverified treatment:** this is the primary anti-hallucination signal (PRD §10) and must be a visually distinct badge/label on every citation, not just a data attribute — e.g. a "Verified source" badge (with source title + link) vs. an "Unverified / general principle" badge (no clickable link implied, since there is no real source to link to). The two states must never look visually similar enough to be confused at a glance.
- **Missing clauses:** rendered as their own list, each with the clause name and a recommendation — visually distinct from flags (missing clauses are absences, not issues found in existing text).
- **Action items:** a short, scannable list of concrete next steps, rendered after flags/missing clauses.
- **Disclaimer:** fixed, always-visible text near the top of the report (see §5's global placement rule) — not a dismissible banner, since PRD frames this as a standing notice, not a one-time alert.
- **Navigation from status → report:** `/documents/[id]` transitions to `/reports/[id]` only once status is `analyzed`; there is no route that shows a partial/in-progress report.

## 8. Voice UI

Per `SYSTEM_DESIGN.md` §10, voice is **Phase 4** — later than the core upload → analyze → report path (Phases 1–3). This section describes the target UI; whether it is hidden, disabled, or simply not yet built is an MVP-scope decision left to §12.

- **"Listen to summary":** a play control on `/reports/[id]` that calls `POST /api/voice/speak` with the report summary text and plays the returned audio via a standard HTML5 `<audio>`-backed player (play/pause, progress). No transcript-editing or scrubbing-heavy player is needed.
- **Voice Q&A ("ask"):** mic via **browser Web Speech API** plus a typed-question field. Chrome is the demo browser. Do **not** call `/api/voice/transcribe` (501 / unused). Show the transcript (or typed text), submit to `POST /api/voice/ask`, and display the grounded answer (text, and optionally spoken via the same `speak` flow). The UI must not imply the answer does new legal research — it is explicitly grounded only in the existing report and its citations (PRD §6.5, FR-25); no "searching the web" or "consulting a lawyer" language or imagery should appear anywhere in this flow.
- **TODO (TKT-032 — implement only after `/reports/[id]` exists):** `Use window.SpeechRecognition || window.webkitSpeechRecognition; onresult → set question text; submit to /api/voice/ask`. Full mic UI waits until the report page exists (TKT-020).
- **STT decision (TKT-027 / FE-OQ-1 resolved):** Wispr is not used; Web Speech is the primary (only) STT path; typed input is always available.

## 9. Component Inventory

Presentational (no data fetching, receive props):

| Component | Used on | Notes |
|---|---|---|
| `RiskBadge` | `/dashboard`, `/reports/[id]` | Maps `risk_score` to green/yellow/red |
| `FlagList` / `FlagCard` | `/reports/[id]` | Renders one flag: clause, issue, severity, citations |
| `CitationBadge` | inside `FlagCard` | Verified vs. unverified visual treatment (§7) |
| `MissingClauseList` | `/reports/[id]` | Clause name + recommendation |
| `ActionItemList` | `/reports/[id]` | Simple ordered/unordered list |
| `DocumentCard` | `/dashboard` | Filename, doc type, status, risk badge, delete control |
| `ProcessingStepper` | `/documents/[id]` | Pipeline stage indicator |
| `UploadDropzone` | `/upload` | Drag-and-drop + browse fallback, file type/size client-side pre-check |
| `AudioPlayer` | `/reports/[id]` | Wraps `speak` response playback |
| `VoiceAsk` | `/reports/[id]` | Mic control + transcript + answer display |
| `Disclaimer` | `/reports/[id]` | Fixed "not legal advice" notice |

Container (data-fetching / stateful, typically route-level or a thin wrapper):

| Component | Responsibility |
|---|---|
| `AuthGate` | Redirect logic described in §5 |
| Route page components (`app/dashboard/page.tsx`, etc.) | Fetch via `lib/api.ts`, handle loading/error, render presentational components |

This inventory is intentionally lean — extract a shared component only once a pattern repeats 3+ times, per the workspace frontend rule; do not build a generic design system.

## 10. Data / Client State

- **Token storage (assumption, not yet decided by backend):** store the access token in memory (React context) and persist only a refresh token (or a flag that a session exists) in a way that survives reload — the simplest option compatible with "persist across reloads" (PRD §6.1) without extra libraries is `localStorage` for both tokens, refreshing the access token on app load via `POST /api/auth/refresh`. This is called out as an **assumption**, not a decision: an httpOnly-cookie-based session would be more secure against XSS but requires backend cookie-setting support that isn't specified yet. See §14 Open Questions.
- **Document list "cache":** no global state library (per workspace rule against Redux/Zustand). `/dashboard` simply refetches `GET /api/documents` on mount and after a delete; no cross-route cache layer is needed at this scale.
- **Polling interval/stop conditions for `/documents/[id]`:** poll `GET /api/documents/{id}` on a fixed interval (recommend starting at 3–5 seconds; exact value is an assumption, see §14) while status is `uploaded` or `processing`. Stop polling once status is `analyzed` (redirect to report) or if a terminal failure status is introduced. Always stop polling when the component unmounts.
- **`lib/api.ts` / `lib/types.ts`:** all backend calls go through a single fetch wrapper (per the workspace frontend rule) reading `NEXT_PUBLIC_API_URL`; response types in `lib/types.ts` mirror the backend's Pydantic schemas and must be updated in the same task as any backend schema change (e.g. when `schemas.py`'s flat `citation: str` becomes a nested `citations[]` with `verified`, per `SYSTEM_DESIGN.md` §5).

## 11. Responsive & Accessibility

- **Responsive:** all screens must work on both mobile and desktop widths. `/upload`'s dropzone and `/reports/[id]`'s flag list are the two layouts most likely to need explicit mobile treatment (stacked single-column below a breakpoint rather than any multi-column layout).
- **Keyboard & labels:**
  - `UploadDropzone` must have a keyboard-operable fallback (a real `<input type="file">` triggered by a labeled button), not a drag-only interaction.
  - The mic button (`VoiceAsk`) must have a clear accessible label (e.g. "Ask a question by voice") and a visible focus state, with start/stop recording operable via keyboard (Enter/Space), not only by mouse/touch.
  - All form inputs (`/login`, `/signup`, `/upload`) have associated `<label>`s, not placeholder-only labeling.
- **WCAG conformance level:** not specified. PRD OQ-4 leaves the target conformance level (e.g. WCAG AA) open; this spec does not invent one — see §14.

## 12. MVP UI Scope vs Later

Mirrors `SYSTEM_DESIGN.md` §10 phasing, restated as which parts of this spec are buildable in each phase:

| Phase | UI scope |
|---|---|
| **1 — Foundation** | `/login`, `/signup`, `/dashboard` (list + upload CTA, no report content yet), `/upload`, `/documents/[id]` shell (status only, stages can be a simple label before the full stepper) |
| **2 — Core analysis** | `/reports/[id]` renders risk score, flags, missing clauses, action items — **without** citation verified/unverified treatment yet (backend doesn't have citations yet) |
| **3 — Grounding** | `/reports/[id]` adds the citation list and the verified/unverified badge treatment (§7) |
| **4 — Voice** | §8's "Listen to summary" and voice Q&A become active; before this phase, those controls should be hidden or omitted entirely, not shown disabled with no explanation |
| **5 — Deployment & hardening** | No new screens; polish pass on error states, disclaimer prominence, and any rate-limit-driven UI (e.g. a friendly message if upload/analyze is rate-limited) |

## 13. Out of Scope

- Any UI for document types other than `rental`/`employment`, or jurisdictions other than India (PRD §4 Non-Goals).
- A lawyer-chat or lawyer-marketplace UI, or any UI implying Lexo is a substitute for a licensed lawyer.
- Multi-party / collaborative review UI (e.g. sharing a report with a landlord or employer).
- Redlining or negotiation-support UI.
- An admin console or any staff-facing tooling.
- Social login UI (PRD §14 Assumptions — email/password only for MVP).
- A visual design system / component library beyond the lean inventory in §9.

## 14. Open Questions

Carried forward from `PRD.md` §14 plus frontend-specific gaps identified while writing this spec. None of these are resolved here — implementers should confirm before building the affected part.

| # | Question | Affects |
|---|---|---|
| FE-OQ-1 (= PRD OQ-1) | **Resolved (TKT-027):** no Wispr; mic uses browser Web Speech API; typed fallback; submit text to `/api/voice/ask`. | §8 Voice UI, Phase 4 |
| FE-OQ-2 (= PRD OQ-4) | What accessibility conformance level (e.g. WCAG AA) is targeted? | §11 Responsive & Accessibility |
| FE-OQ-3 (= PRD OQ-6) | Is password reset UI required for MVP `/login`, or deferred? | §6.1 `/login` |
| FE-OQ-4 | What is the exact file size limit (and copy) to show on upload rejection? | §6.4 `/upload` |
| FE-OQ-5 | What is the backend's recommended/actual polling interval for `/api/documents/{id}`, and does it expose a distinct "failed" status the status screen should render? | §6.5 `/documents/[id]`, §10 |
| FE-OQ-6 | Where should access/refresh tokens be stored — client-side (`localStorage`/memory) as assumed in §10, or httpOnly cookies set by the backend? This changes how `lib/api.ts` attaches auth to requests. | §10 Data / Client State |
| FE-OQ-7 | `lexo/frontend/.env.local.example` currently duplicates backend secrets and omits `NEXT_PUBLIC_API_URL` (§3) — confirm this is simply stale and schedule the fix; not a design question, but an unresolved cleanup item. | §3 Tech Baseline |
