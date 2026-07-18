# Lexo — Product Requirements Document

## 1. Document Control

| Field | Value |
|---|---|
| Status | **Draft** |
| Product | Lexo — AI legal-document assistant (rental & employment agreements, India) |
| Related docs | [`ARCHITECTURE.md`](./ARCHITECTURE.md) (high-level flow, optional voice path), [`SYSTEM_DESIGN.md`](./SYSTEM_DESIGN.md) (architecture, data model, API contract, security, phased build plan), [`FRONTEND_SPEC.md`](./FRONTEND_SPEC.md) (frontend routes, screen states, and UI behavior), [`SECURITY_AND_ACCESS.md`](./SECURITY_AND_ACCESS.md) (access control, auth, data protection, security acceptance criteria) |
| Scope of this doc | Product requirements only. Technical diagrams, the full API contract, and the full data model live in `SYSTEM_DESIGN.md` and are referenced, not duplicated, below. |

This PRD assumes the reader has skimmed `ARCHITECTURE.md` for the overall flow. Where a requirement depends on a technical constraint (e.g. async processing, storage encryption), it links to the relevant `SYSTEM_DESIGN.md` section instead of restating it.

## 2. Executive Summary

Lexo is an AI-powered assistant that helps everyday people — tenants and employees in India — understand rental and employment agreements before they sign them. A user uploads a document, and Lexo extracts and classifies its clauses, flags risky or unusual terms, identifies protections the document is missing, and produces a plain-language risk report. Every legal claim in the report is either backed by a real, retrievable citation (via Exa) or explicitly labeled as an unverified general principle — Lexo never invents a statute or section number. The report is also available as speech, and users can ask follow-up questions by voice, making the product usable by people less comfortable with dense legal text.

## 3. Problem Statement

Rental and employment agreements in India are frequently one-sided, and the people who sign them are rarely lawyers. They cannot easily tell whether a security deposit clause is unusually high, whether a notice period is unfair, or whether a standard protection (like a deposit refund timeline or statutory benefit mention) is simply missing from the document. Hiring a lawyer to review a routine agreement is disproportionately expensive and slow relative to the decision being made. The result is that people sign documents they don't fully understand, discovering unfavorable terms only after a dispute arises.

Lexo closes this gap by giving non-lawyers a fast, plain-language, evidence-backed second opinion before they sign — without claiming to replace a lawyer, and without ever fabricating legal authority to sound more convincing.

## 4. Goals & Non-Goals

### Goals

- Let a non-lawyer upload a rental or employment agreement and receive a plain-language risk report in minutes.
- Flag risky or unusual clauses and missing protections, each explained in accessible language.
- Ground every legal citation in a real, retrievable source; explicitly label anything that can't be grounded as "unverified / general principle."
- Make the report accessible by voice (listen to the summary; ask follow-up questions by voice).
- Let users build a private history of past documents/reports and delete any of their data on demand.
- Carry an explicit "not legal advice" disclaimer on every report and every relevant API response.

### Non-Goals (for MVP; see §15 for future consideration)

- Document types other than rental and employment agreements.
- Jurisdictions other than India.
- Acting as, or being positioned as, a substitute for a licensed lawyer.
- Real-time legal advice or negotiation support (e.g. redlining, contract negotiation on the user's behalf).
- Multi-party collaboration features (e.g. sharing a report with a landlord or employer for negotiation).
- Guaranteeing legal citations exist for every flag — when no reliable source is found, the product's job is to say so, not to keep searching indefinitely or to guess.

## 5. Target Users / Personas & Jobs-to-be-Done

Lexo serves two primary personas, matching the two supported `doc_type` values. These personas are authored for this PRD (not sourced verbatim from `SYSTEM_DESIGN.md`) and should be corrected if they don't match actual target users.

| Persona | Description | Jobs-to-be-Done |
|---|---|---|
| **Riya, prospective tenant** | About to sign a rental agreement for an apartment; not a lawyer; wants to move in without being surprised later by a bad deposit or notice clause. | "When I'm about to sign a rental agreement, I want to know if anything in it is unusual or risky, so I can raise it with the landlord or broker before I sign, not after." |
| **Arun, new or exiting employee** | Reviewing an offer letter or exit terms; wants to understand notice pay, non-compete, and termination clauses without paying for a lawyer for a routine review. | "When I get an offer letter or resignation paperwork, I want a quick, honest read on what's fair and what's missing, so I don't sign away rights I didn't know I had." |

Both personas share a underlying job: *"Help me understand what I'm about to sign, in language I understand, without making me guess whether the legal claims are real."*

## 6. User Journeys / Use Cases

The journeys below describe user-facing behavior only. For the corresponding API calls and pipeline stages, see `SYSTEM_DESIGN.md` §4 (pipeline sequence diagram) and §6 (API contract).

### 6.1 Sign up / log in

The user creates an account with email and password, or logs back in. On success, they land on the dashboard. Sessions persist via access/refresh tokens so the user isn't asked to log in on every visit within a reasonable window.

### 6.2 Upload a document

From the dashboard, the user starts a new upload, selects the document type (rental or employment), and provides a file (PDF or DOCX). The system validates the file type/size and confirms the upload succeeded, then offers to start analysis.

### 6.3 Analyze

The user starts analysis and sees a status view that progresses through visible stages (e.g. extracting → analyzing → grounding) rather than a silent spinner, so they know the system is working and roughly how far along it is.

### 6.4 View report

Once analysis completes, the user sees a report with: an overall risk badge (green/yellow/red), a list of flagged clauses with plain-language explanations and citations (each marked verified or unverified), a list of missing protections with recommendations, and a list of action items. A "not legal advice" disclaimer is visible on the report.

### 6.5 Voice: listen and ask

From the report, the user can play an audio summary of the report, and can ask a follow-up question by voice. The spoken answer is grounded only in the analyzed document and its existing citations — it does not introduce new legal claims beyond what the report already established.

### 6.6 History

The user returns to the dashboard and sees a list of their previously uploaded documents with status and risk badge, and can open any past report again.

### 6.7 Delete

The user can delete a document from their history. Deleting removes the uploaded file, the document record, and its associated report, flags, citations, missing clauses, and action items — nothing is left behind, and no other user is ever able to see or delete another user's data.

## 7. Functional Requirements

Priority uses MoSCoW (MUST / SHOULD / COULD). Requirements are grouped by epic. None of these are implemented yet as of this PRD's drafting — see §11 for phasing and current build status.

### 7.1 Auth

| # | Requirement | Priority |
|---|---|---|
| FR-1 | User can create an account with email and password. | MUST |
| FR-2 | User can log in and receive a session that persists across page reloads without re-entering credentials every time. | MUST |
| FR-3 | User can log out, ending their session. | MUST |
| FR-4 | System must never allow one user's session to access another user's documents or reports. | MUST |
| FR-5 | User can recover access if they forget their password. | COULD |

### 7.2 Upload

| # | Requirement | Priority |
|---|---|---|
| FR-6 | User can select a document type (rental or employment) before or during upload. | MUST |
| FR-7 | User can upload a PDF or DOCX file. | MUST |
| FR-8 | System must reject files exceeding a defined size limit or of an unsupported type, with a clear error message. | MUST |
| FR-9 | User can see confirmation that the upload succeeded before starting analysis. | MUST |

### 7.3 Analysis

| # | Requirement | Priority |
|---|---|---|
| FR-10 | User can trigger analysis of an uploaded document. | MUST |
| FR-11 | User can see the current processing stage while analysis is in progress (not just a generic loading state). | SHOULD |
| FR-12 | System must extract text from digital PDFs/DOCX, and fall back to image-based understanding for scanned/low-text-density pages. | MUST |
| FR-13 | System must classify the document's clauses using a taxonomy specific to the selected document type (rental vs. employment). | MUST |
| FR-14 | System must evaluate clauses against known risk patterns and produce a plain-language issue description and severity for each flag. | MUST |
| FR-15 | System must check the document against a per-document-type checklist of expected protections and report which are missing. | MUST |

### 7.4 Report & grounding

| # | Requirement | Priority |
|---|---|---|
| FR-16 | User can view a report with an overall risk score (green/yellow/red). | MUST |
| FR-17 | User can view each flag with its plain-language explanation, severity, and supporting citation(s). | MUST |
| FR-18 | System must attach a real, retrievable citation to a flag whenever one can be found via Exa, filtered to trusted legal/government sources. | MUST |
| FR-19 | System must explicitly label a flag or missing clause as "unverified / general principle" when no reliable citation can be found, rather than fabricating one. | MUST |
| FR-20 | User can view missing-protection items with a recommendation for each. | MUST |
| FR-21 | User can view a list of concrete action items derived from the report. | MUST |
| FR-22 | Every report view must display a "this is not legal advice" disclaimer. | MUST |

### 7.5 Voice

| # | Requirement | Priority |
|---|---|---|
| FR-23 | User can play an audio version of the report summary. | SHOULD |
| FR-24 | User can ask a spoken follow-up question about their report and receive a spoken (and/or text) answer. | SHOULD |
| FR-25 | System must ground voice Q&A answers only in the analyzed document and its existing report/citations — no new claims beyond what's already established. | MUST (if voice Q&A is enabled) |
| FR-26 | If the primary voice-input provider has no usable server-side API (see §14 open question), system should offer a fallback voice-input path (e.g. browser-based speech recognition) so the feature still works. | SHOULD |

### 7.6 History & data control

| # | Requirement | Priority |
|---|---|---|
| FR-27 | User can see a list of their own past documents with status and risk badge. | MUST |
| FR-28 | User can reopen any of their own past reports. | MUST |
| FR-29 | User can delete a document, which removes the file, the document record, and all associated report data. | MUST |
| FR-30 | System must never expose another user's documents or reports through any endpoint. | MUST |

## 8. Non-Functional Requirements

| Category | Requirement | Notes |
|---|---|---|
| **Security** | All traffic must be served over HTTPS. | See `SYSTEM_DESIGN.md` §7 |
| **Security** | Passwords must be hashed, never stored or logged in plaintext. | See `SYSTEM_DESIGN.md` §7 |
| **Security** | Uploaded files must be stored with server-side encryption at rest; raw storage URLs must never be exposed directly to the client. | See `SYSTEM_DESIGN.md` §3.3, §7 |
| **Privacy / data isolation** | Every query for documents, reports, flags, or citations must be scoped to the authenticated user; users cannot read or delete another user's data. | See `SYSTEM_DESIGN.md` §7 |
| **Privacy / right to delete** | Deleting a document must cascade to its file, report, flags, citations, missing clauses, and action items — no orphaned data. | See `SYSTEM_DESIGN.md` §5, §7 |
| **Performance** | Upload and analysis are asynchronous; the user must never be blocked on a long-running synchronous request, and must be able to see progress. | Exact latency targets are an **Open Question** (§14) |
| **Rate limiting** | Upload and analyze endpoints must be rate-limited per user to bound LLM/Exa cost exposure and abuse. | Specific thresholds are an **Open Question** (§14) |
| **Accessibility** | Voice input/output must be available as an alternative to reading/typing dense text. | Formal conformance level (e.g. WCAG AA) is an **Open Question** (§14) |
| **Trust & disclosure** | Every report (UI and API) must carry an explicit "not legal advice" disclaimer. | See `SYSTEM_DESIGN.md` §7 |
| **Anti-hallucination** | The system must never present a fabricated statute, section number, or citation as if it were real. | Core product principle, see `SYSTEM_DESIGN.md` §1 |

## 9. Screens / Information Architecture

| Screen | Purpose |
|---|---|
| `/login` | Existing user signs in. |
| `/signup` | New user creates an account. |
| `/dashboard` | Lists the user's past documents/reports with status and risk badge; entry point to a new upload. |
| `/upload` | Select document type, choose/drag-and-drop a file, submit for analysis. |
| `/documents/[id]` | Shows processing status/progress for a document being analyzed. |
| `/reports/[id]` | Displays the full report: risk badge, flags with citations, missing clauses, action items, audio summary playback, voice Q&A entry point. |

This matches the screen list in `SYSTEM_DESIGN.md` §3.1. As of this PRD's drafting, the frontend contains only a placeholder home page (`lexo/frontend/app/page.tsx`) — none of the above screens exist yet (see §11).

## 10. Product-Facing Report Contract

This section describes the report at a product level — what a user sees and what each field means to them. It intentionally does not restate the full Pydantic models or ER diagram; see `SYSTEM_DESIGN.md` §5 for the authoritative schema and `SYSTEM_DESIGN.md` §6 for the API contract.

| Field (product meaning) | User-facing description |
|---|---|
| `risk_score` | Overall risk badge for the document: green (low concern), yellow (some concerns), or red (significant concerns). |
| `flags[]` | Individual issues found in specific clauses, each with a plain-language explanation and a severity level. |
| `flags[].citations[].verified` | Whether the citation attached to a flag is a real, retrieved source (`true`) or the flag is labeled "unverified / general principle" because no reliable source was found (`false`). This distinction must always be visible to the user, not just present in the data. |
| `missing_clauses[]` | Protections the document should typically include for its type (rental/employment) but doesn't, each with a recommendation. |
| `action_items[]` | Concrete next steps the user can take based on the report (e.g. "ask the landlord to clarify the deposit refund timeline"). |

**Product requirement:** the `verified` distinction on citations must be visually distinguishable in the UI (e.g. a badge or label), not just a data field — this is the primary anti-hallucination safeguard surfaced to the user, per the core design principle in `SYSTEM_DESIGN.md` §1.

## 11. MVP Scope & Phasing

Phasing follows `SYSTEM_DESIGN.md` §10 exactly, restated here as product-visible outcomes rather than implementation tasks.

| Phase | Product outcome |
|---|---|
| **1 — Foundation** | Users can sign up, log in, and upload a document; it appears in their dashboard with a status. No analysis yet. |
| **2 — Core analysis** | Uploaded documents can be analyzed; users see a full report (risk score, flags, missing clauses, action items) — without citations yet. |
| **3 — Grounding** | Flags and missing clauses in the report carry real citations where available, and are explicitly labeled "unverified / general principle" otherwise. |
| **4 — Voice** | Users can listen to a report summary and ask spoken follow-up questions. |
| **5 — Deployment & hardening** | Product is live on Render with rate limiting, delete/retention flows, and disclaimers fully in place. |

**Current build status (as of this PRD):** all backend routes (`/api/upload`, `/api/analyze`, `/api/voice`) return `501 Not Implemented`; no auth, database wiring, or storage integration exists yet; the frontend has no screens beyond a placeholder home page. The product is pre-Phase-1 relative to this phasing table. This PRD describes target behavior; it does not claim any phase is complete.

## 12. Acceptance Criteria

Testable, per epic. These define "done" for each functional area described in §7.

### Auth
- [ ] User can sign up with a valid email/password and is redirected to the dashboard.
- [ ] User cannot sign up twice with the same email.
- [ ] User can log in with correct credentials and cannot log in with incorrect ones.
- [ ] A logged-in user's session persists across a page reload without re-authentication.
- [ ] A logged-in user cannot fetch another user's document or report by guessing/changing an id in a request.

### Upload
- [ ] User can upload a valid PDF or DOCX and receive a document id.
- [ ] User selecting "rental" or "employment" as `doc_type` is reflected in how the document is later analyzed.
- [ ] Uploading a file of an unsupported type or over the size limit is rejected with a clear, user-visible error.

### Analysis
- [ ] Triggering analysis on an uploaded document moves it out of "uploaded" status and eventually to a completed state.
- [ ] A scanned/low-text document still produces a report (via the multimodal fallback), not a failure.
- [ ] The report's flags reference clause types appropriate to the selected `doc_type` (e.g. non-compete only flagged for employment documents).

### Report & grounding
- [ ] Every flag shown to the user has an explanation in plain language, not legal jargon alone.
- [ ] Every flag/missing-clause citation is visibly marked verified or unverified — never presented as a real citation when it isn't.
- [ ] The report displays an overall risk badge and a "not legal advice" disclaimer.
- [ ] Deleting a document also removes its report, flags, citations, missing clauses, and action items (verified via a subsequent fetch returning not-found).

### Voice
- [ ] User can play an audio summary of a completed report.
- [ ] User can ask a spoken question and receive an answer that does not introduce claims absent from the underlying report.
- [ ] If the primary STT provider is unavailable, a fallback voice-input path still lets the user submit a spoken question (see §14 open question).

### History & data control
- [ ] Dashboard lists only the current user's documents, each with correct status and risk badge.
- [ ] User can reopen any of their own past reports and see the same content as originally generated.
- [ ] User can delete a document from the dashboard and it no longer appears afterward.

## 13. Success Metrics

No live usage exists yet, so these are MVP-realistic proxy metrics intended for early post-launch tracking rather than targets with historical baselines. They are new synthesis for this PRD and should be revisited once real usage data exists.

| Metric | What it tells us |
|---|---|
| Upload → completed-report conversion rate | Whether the pipeline reliably finishes what users start. |
| % of flags with a verified (non-"unverified") citation | Whether grounding is working well enough to be genuinely useful, not just safe. |
| Report-to-action-item engagement (e.g. action items viewed/expanded) | Whether users find the output actionable, not just informational. |
| Voice feature usage rate among users who open a report | Whether the accessibility investment (voice in/out) is actually used. |
| Delete-flow usage / support requests about data | Whether users trust and exercise their privacy controls, and whether the flow is discoverable. |
| Disclaimer visibility (qualitative, e.g. usability testing) | Whether users understand the "not legal advice" boundary, not just whether it's technically present. |

## 14. Risks, Assumptions, Open Questions

### Risks

| Risk | Mitigation |
|---|---|
| Grounding step fails to find sources often enough that most flags end up "unverified," undermining trust in the product's core value proposition. | Track the verified-citation rate (§13) closely post-launch; revisit trusted-domain list and query generation if too low. |
| Users misread "informational analysis" as formal legal advice despite the disclaimer. | Disclaimer must be prominent (not buried in fine print) — a UX/copy concern, not just a data field (see §10). |
| Voice Q&A drifts into generating new legal claims not grounded in the existing report. | FR-25 explicitly constrains voice answers to the analyzed document + existing citations; should be covered by acceptance testing. |
| Treating the current backend/frontend scaffold as further along than it is, leading to over-promising a launch date. | §11 explicitly states current build status is pre-Phase-1. |

### Assumptions

- Users have a PDF or DOCX copy of their agreement available to upload (no support for photos of physical documents beyond what the scanned-page/OCR fallback handles).
- Users are comfortable providing an email/password; no social login is assumed for MVP.
- India is the sole jurisdiction; citation grounding trusted-domain filtering (`SYSTEM_DESIGN.md` §4) assumes Indian legal/government sources.

### Open Questions (do not invent answers — resolve before the relevant phase)

| # | Question | Blocks |
|---|---|---|
| OQ-1 | Does Wispr Flow expose a server-callable STT API, or must Lexo rely on a fallback (e.g. browser Web Speech API) for voice input? Flagged explicitly in `SYSTEM_DESIGN.md` §11 as unconfirmed. | Phase 4 (Voice) |
| OQ-2 | The root [`README.md`](../../README.md) names the project "VectorMinds," while all product docs and code refer to "Lexo." Which name is canonical — is a rename needed, or is "VectorMinds" an unrelated/legacy artifact? | Branding consistency, not a build blocker |
| OQ-3 | What are the concrete rate-limit thresholds for upload/analyze endpoints (requests per user per time window)? | Phase 5 (hardening) |
| OQ-4 | What accessibility conformance level (e.g. WCAG AA) is targeted beyond voice in/out? | Phase 5 (hardening) / ongoing frontend work |
| OQ-5 | Are there specific latency/SLA targets for analysis completion (e.g. "under N minutes for an M-page document")? | Performance validation, Phase 2 onward |
| OQ-6 | Is password reset (FR-5) required for MVP, or acceptable to defer? | Phase 1 scope |

## 15. Out of Scope / Future

The following are explicitly **not** part of this PRD's scope and are not committed to any phase above. They may be considered in the future but should not be assumed or built against without a PRD update:

- Document types beyond rental and employment agreements (e.g. loan agreements, NDAs, vendor contracts).
- Jurisdictions beyond India.
- Languages beyond what the current text-extraction/LLM pipeline supports natively (no dedicated localization scope defined).
- Multi-party / collaborative review (sharing a report for negotiation with a landlord, HR, or counterparty).
- Graduating the async pipeline from FastAPI `BackgroundTasks` to a dedicated queue (Celery + Redis, or a Render Background Worker) — noted in `SYSTEM_DESIGN.md` §4/§8 as a future option, not required unless load demands it.
- Any feature that would require the product to give a definitive legal conclusion rather than a flagged-for-review, plain-language analysis.
