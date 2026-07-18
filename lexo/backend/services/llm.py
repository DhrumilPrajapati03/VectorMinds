"""Gemini analysis service: clause segmentation, risk flags, missing-clause diff.

Pure service — no FastAPI routes, no DB writes. Callers pass extracted text +
doc_type; returns a validated AnalysisResult. Citations stay empty (Phase 3 / Exa).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from models.schemas import (
    ActionItemOut,
    AnalysisResult,
    ClauseSegment,
    Flag,
    MissingClauseItem,
    ReportRead,
)

logger = logging.getLogger(__name__)

GEMINI_ANALYSIS_MODEL = "gemini-1.5-flash"
DocType = Literal["rental", "employment"]
VALID_DOC_TYPES: frozenset[str] = frozenset({"rental", "employment"})
VALID_RISK_SCORES: frozenset[str] = frozenset({"green", "yellow", "red"})
VALID_SEVERITIES: frozenset[str] = frozenset({"high", "medium", "low"})
VALID_PRIORITIES: frozenset[str] = frozenset({"high", "medium", "low"})

# Fixed taxonomies — SYSTEM_DESIGN.md §4 step 3.
RENTAL_CLAUSE_TAXONOMY: tuple[str, ...] = (
    "rent_amount",
    "security_deposit",
    "deposit_refund",
    "notice_period",
    "lock_in_period",
    "maintenance",
    "subletting",
    "termination",
    "indemnity",
    "utilities",
    "other",
)

EMPLOYMENT_CLAUSE_TAXONOMY: tuple[str, ...] = (
    "compensation",
    "notice_period",
    "notice_pay",
    "termination",
    "non_compete",
    "non_solicit",
    "confidentiality",
    "statutory_benefits",
    "probation",
    "indemnity",
    "other",
)

# Missing-clause checklists — SYSTEM_DESIGN.md §4 step 5.
RENTAL_MISSING_CHECKLIST: tuple[str, ...] = (
    "deposit refund timeline",
    "notice period",
    "lock-in period",
    "maintenance responsibility",
    "subletting rights",
)

EMPLOYMENT_MISSING_CHECKLIST: tuple[str, ...] = (
    "notice pay",
    "non-compete/non-solicit reasonableness",
    "termination cause",
    "statutory benefits (PF/gratuity mention)",
)

RENTAL_RISK_PATTERNS = (
    "Security deposit far above Model Tenancy Act guidance (often >2–3 months rent).",
    "No or vague deposit refund timeline after vacating.",
    "One-sided termination (landlord can end easily; tenant cannot).",
    "Very long lock-in with heavy early-exit penalties.",
    "Tenant solely liable for structural/major maintenance.",
    "Blanket ban on subletting with no consent path.",
)

EMPLOYMENT_RISK_PATTERNS = (
    "Broad non-compete that may be void/unenforceable under Indian Contract Act §27 "
    "(treat as a risk pattern to flag in plain language — do NOT invent verified citations).",
    "Notice period or notice pay heavily one-sided against the employee.",
    "Termination without cause / at-will style wording with weak employee protection.",
    "Missing or vague PF / gratuity / statutory benefit mentions where expected.",
    "Overbroad non-solicit (clients + employees, long duration, wide geography).",
)


class AnalysisError(Exception):
    """Raised when document analysis cannot complete cleanly."""


# --- Gemini JSON shape (citations omitted; we force empty on normalize) ---


class _RawClause(BaseModel):
    clause_type: str
    text: str
    clause_ref: str = ""


class _RawFlag(BaseModel):
    clause_ref: str
    issue: str
    severity: str
    category: str = ""

    @field_validator("severity")
    @classmethod
    def normalize_severity(cls, v: str) -> str:
        s = (v or "").strip().lower()
        aliases = {
            "critical": "high",
            "severe": "high",
            "red": "high",
            "moderate": "medium",
            "yellow": "medium",
            "minor": "low",
            "info": "low",
            "green": "low",
        }
        s = aliases.get(s, s)
        if s not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {sorted(VALID_SEVERITIES)}")
        return s


class _RawMissing(BaseModel):
    clause_name: str
    recommendation: str


class _RawAction(BaseModel):
    text: str
    priority: str = "medium"

    @field_validator("priority")
    @classmethod
    def normalize_priority(cls, v: str) -> str:
        p = (v or "").strip().lower()
        aliases = {"critical": "high", "urgent": "high", "normal": "medium", "low": "low"}
        p = aliases.get(p, p)
        if p not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}")
        return p


class _RawAnalysis(BaseModel):
    summary: str
    risk_score: str
    clauses: list[_RawClause] = Field(default_factory=list)
    flags: list[_RawFlag] = Field(default_factory=list)
    missing_clauses: list[_RawMissing] = Field(default_factory=list)
    action_items: list[_RawAction] = Field(default_factory=list)

    @field_validator("risk_score")
    @classmethod
    def normalize_risk_score(cls, v: str) -> str:
        score = (v or "").strip().lower()
        if score not in VALID_RISK_SCORES:
            raise ValueError("risk_score must be green, yellow, or red")
        return score


def analyze_document(text: str, doc_type: str) -> AnalysisResult:
    """Segment clauses, flag risks, and diff missing-clause checklists via Gemini.

    Args:
        text: Extracted plain-text document body.
        doc_type: ``rental`` or ``employment``.

    Returns:
        Validated ``AnalysisResult`` (citations always empty — Phase 3).

    Raises:
        AnalysisError: invalid inputs, missing API key, Gemini failure, or
            unparseable model output after one retry.
    """
    normalized_type = _validate_doc_type(doc_type)
    body = (text or "").strip()
    if not body:
        raise AnalysisError("Document text is empty; nothing to analyze")

    api_key = _require_gemini_api_key()
    prompt = _build_prompt(body, normalized_type)

    try:
        raw = _call_gemini_json(api_key, prompt, attempt=1)
        result = _parse_and_normalize(raw, normalized_type)
        logger.info(
            "analyze_document ok doc_type=%s flags=%s missing=%s risk=%s",
            normalized_type,
            len(result.flags),
            len(result.missing_clauses),
            result.risk_score,
        )
        return result
    except AnalysisError:
        logger.info("analyze_document failed doc_type=%s (first attempt)", normalized_type)
        raise
    except (ValidationError, json.JSONDecodeError, ValueError) as first_exc:
        logger.info(
            "analyze_document invalid JSON/schema on first attempt; retrying once (%s)",
            type(first_exc).__name__,
        )
        try:
            raw = _call_gemini_json(api_key, prompt, attempt=2)
            result = _parse_and_normalize(raw, normalized_type)
            logger.info(
                "analyze_document ok after retry doc_type=%s flags=%s missing=%s risk=%s",
                normalized_type,
                len(result.flags),
                len(result.missing_clauses),
                result.risk_score,
            )
            return result
        except AnalysisError:
            raise
        except (ValidationError, json.JSONDecodeError, ValueError) as second_exc:
            logger.info(
                "analyze_document failed after retry (%s)",
                type(second_exc).__name__,
            )
            raise AnalysisError(
                "Gemini returned invalid analysis JSON after retry. "
                "Check model output and try again."
            ) from second_exc


def _validate_doc_type(doc_type: str) -> DocType:
    value = (doc_type or "").strip().lower()
    if value not in VALID_DOC_TYPES:
        raise AnalysisError(
            f"doc_type must be 'rental' or 'employment', got {doc_type!r}"
        )
    return value  # type: ignore[return-value]


def _require_gemini_api_key() -> str:
    # Lazy import: missing key must not crash app import; only fails at call time.
    from config import settings

    key = (settings.gemini_api_key or "").strip()
    if not key:
        raise AnalysisError(
            "GEMINI_API_KEY is required for document analysis. "
            "Set GEMINI_API_KEY in lexo/backend/.env."
        )
    return key


def _taxonomy_for(doc_type: DocType) -> tuple[str, ...]:
    if doc_type == "rental":
        return RENTAL_CLAUSE_TAXONOMY
    return EMPLOYMENT_CLAUSE_TAXONOMY


def _checklist_for(doc_type: DocType) -> tuple[str, ...]:
    if doc_type == "rental":
        return RENTAL_MISSING_CHECKLIST
    return EMPLOYMENT_MISSING_CHECKLIST


def _risk_patterns_for(doc_type: DocType) -> tuple[str, ...]:
    if doc_type == "rental":
        return RENTAL_RISK_PATTERNS
    return EMPLOYMENT_RISK_PATTERNS


def _build_prompt(text: str, doc_type: DocType) -> str:
    taxonomy = ", ".join(_taxonomy_for(doc_type))
    checklist = "\n".join(f"- {item}" for item in _checklist_for(doc_type))
    patterns = "\n".join(f"- {p}" for p in _risk_patterns_for(doc_type))

    # Cap prompt size for hackathon latency/cost; keep head + tail of long docs.
    doc_body = text
    max_chars = 60_000
    if len(doc_body) > max_chars:
        half = max_chars // 2
        doc_body = (
            doc_body[:half]
            + "\n\n[... document truncated for analysis ...]\n\n"
            + doc_body[-half:]
        )

    return f"""You are Lexo, an India-focused legal document assistant for everyday people.
Analyze this {doc_type} agreement. Respond with ONLY valid JSON (no markdown fences).

Tasks:
1) Segment the document into typed clauses using ONLY this taxonomy:
   {taxonomy}
2) Flag risky or unusual clauses using these India-focused risk patterns:
{patterns}
   For each flag: plain-language issue a non-lawyer understands; severity high|medium|low;
   category (short label); clause_ref (taxonomy type or short quote pointer).
3) Missing-clause checklist diff — list ONLY checklist items that are absent or
   effectively missing. Use these exact clause_name strings when applicable:
{checklist}
   Each missing item needs a practical recommendation (what to ask for / negotiate).
4) Overall risk_score: exactly one of green | yellow | red.
5) 2–6 concrete action_items with priority high|medium|low.
6) Plain-language summary (2–5 sentences).

Rules:
- Do NOT invent statute citations or URLs as verified facts. Leave citations out entirely.
- Do not claim to be a lawyer or give definitive legal advice; describe risks plainly.
- If a checklist item is clearly present and adequate, do NOT list it as missing.
- Prefer fewer high-quality flags over speculative ones.

Required JSON shape:
{{
  "summary": "string",
  "risk_score": "green|yellow|red",
  "clauses": [
    {{"clause_type": "taxonomy_value", "text": "clause excerpt", "clause_ref": "optional"}}
  ],
  "flags": [
    {{
      "clause_ref": "string",
      "issue": "plain language",
      "severity": "high|medium|low",
      "category": "string"
    }}
  ],
  "missing_clauses": [
    {{"clause_name": "exact checklist name or close match", "recommendation": "string"}}
  ],
  "action_items": [
    {{"text": "string", "priority": "high|medium|low"}}
  ]
}}

DOCUMENT TEXT:
\"\"\"
{doc_body}
\"\"\"
"""


def _call_gemini_json(api_key: str, prompt: str, attempt: int) -> str:
    import google.generativeai as genai

    # Never log the key or full document body.
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_ANALYSIS_MODEL)

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )
    except Exception as exc:
        logger.exception("Gemini analysis call failed (attempt=%s)", attempt)
        raise AnalysisError(
            "Gemini analysis request failed. Check GEMINI_API_KEY and model access."
        ) from exc

    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        raise AnalysisError("Gemini analysis returned empty response")
    return raw


def _extract_json_object(raw: str) -> Any:
    """Parse JSON; tolerate optional markdown fences around the object."""
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: first {...} block.
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _parse_and_normalize(raw: str, doc_type: DocType) -> AnalysisResult:
    data = _extract_json_object(raw)
    if not isinstance(data, dict):
        raise ValueError("analysis JSON root must be an object")

    parsed = _RawAnalysis.model_validate(data)
    flags = [
        Flag(
            clause_ref=f.clause_ref.strip() or "unspecified",
            issue=f.issue.strip(),
            severity=f.severity,
            category=(f.category or "general").strip() or "general",
            citations=[],  # Phase 3 Exa — never invent citations here
        )
        for f in parsed.flags
        if (f.issue or "").strip()
    ]

    checklist = _checklist_for(doc_type)
    checklist_lower = {c.lower(): c for c in checklist}
    missing: list[MissingClauseItem] = []
    seen_missing: set[str] = set()
    for m in parsed.missing_clauses:
        name = (m.clause_name or "").strip()
        if not name:
            continue
        # Prefer canonical checklist wording when the model paraphrases lightly.
        canonical = checklist_lower.get(name.lower(), name)
        key = canonical.lower()
        if key in seen_missing:
            continue
        seen_missing.add(key)
        missing.append(
            MissingClauseItem(
                clause_name=canonical,
                recommendation=(m.recommendation or "").strip()
                or "Ask for this protection to be written into the agreement before signing.",
            )
        )

    actions = [
        ActionItemOut(text=a.text.strip(), priority=a.priority)
        for a in parsed.action_items
        if (a.text or "").strip()
    ]

    clauses = [
        ClauseSegment(
            clause_type=c.clause_type.strip() or "other",
            text=c.text.strip(),
            clause_ref=(c.clause_ref or "").strip(),
        )
        for c in parsed.clauses
        if (c.text or "").strip()
    ]

    risk_score = _aggregate_risk_score(flags, parsed.risk_score)

    return AnalysisResult(
        summary=(parsed.summary or "").strip()
        or "Analysis complete. Review the flags and missing clauses before signing.",
        risk_score=risk_score,  # type: ignore[arg-type]
        flags=flags,
        missing_clauses=missing,
        action_items=actions,
        clauses=clauses,
    )


def _aggregate_risk_score(flags: list[Flag], proposed: str) -> str:
    """Prefer severity rollup when flags exist; otherwise accept Gemini's score."""
    proposed = (proposed or "").strip().lower()
    if proposed not in VALID_RISK_SCORES:
        proposed = "yellow"

    if not flags:
        return proposed if proposed in VALID_RISK_SCORES else "green"

    severities = {f.severity for f in flags}
    if "high" in severities:
        rolled = "red"
    elif "medium" in severities:
        rolled = "yellow"
    else:
        rolled = "yellow" if len(flags) >= 3 else "green"

    # Take the worse of model proposal vs severity rollup.
    order = {"green": 0, "yellow": 1, "red": 2}
    return rolled if order[rolled] >= order.get(proposed, 1) else proposed


def answer_question(report: ReportRead, question: str) -> str:
    """Answer a follow-up using ONLY the existing report (TKT-030).

    Does not invent new legal claims or citations. Declines out-of-scope questions.

    Raises:
        AnalysisError: missing API key, empty question, or Gemini failure.
    """
    q = (question or "").strip()
    if not q:
        raise AnalysisError("Question is empty")

    api_key = _require_gemini_api_key()
    context = _build_report_context(report)
    prompt = f"""You are Lexo, answering a follow-up about an already-analyzed legal document report.
You are NOT a lawyer. This is not legal advice.

STRICT RULES:
- Answer ONLY using the REPORT CONTEXT below (summary, risk score, flags, missing clauses,
  action items, and citations already listed there).
- Do NOT invent new legal claims, statutes, section numbers, or citations.
- Do NOT invent new flags, missing clauses, or action items.
- If a citation is listed, you may mention it; never invent a new URL or source title.
- If the question cannot be answered from the REPORT CONTEXT (out of scope, asking for
  new research, personal legal strategy beyond the report, unrelated topics), explicitly
  decline. Say you can only discuss what is already in this Lexo report, and suggest
  consulting a qualified lawyer for anything beyond that.
- Keep the answer concise (a few short paragraphs at most), plain language for a non-lawyer.

REPORT CONTEXT:
{context}

USER QUESTION:
{q}

Answer:"""

    try:
        answer = _call_gemini_text(api_key, prompt)
    except AnalysisError:
        raise
    except Exception as exc:
        logger.exception("answer_question gemini failed")
        raise AnalysisError(
            "Gemini Q&A request failed. Check GEMINI_API_KEY and model access."
        ) from exc

    cleaned = (answer or "").strip()
    if not cleaned:
        raise AnalysisError("Gemini returned an empty answer")
    logger.info("answer_question ok report_id=%s", report.id)
    return cleaned


def _build_report_context(report: ReportRead) -> str:
    """Serialize report fields for grounded Q&A — no document body, no new claims."""
    lines: list[str] = [
        f"risk_score: {report.risk_score}",
        f"summary: {report.summary}",
        "flags:",
    ]
    if not report.flags:
        lines.append("  (none)")
    for i, flag in enumerate(report.flags, start=1):
        lines.append(
            f"  {i}. [{flag.severity}] {flag.category} | clause_ref={flag.clause_ref}"
        )
        lines.append(f"     issue: {flag.issue}")
        if flag.citations:
            for c in flag.citations:
                verified = "verified" if c.verified else "unverified"
                lines.append(
                    f"     citation ({verified}): {c.source_title} | "
                    f"url={c.source_url or '(none)'} | snippet={c.source_snippet}"
                )
        else:
            lines.append("     citations: (none)")

    lines.append("missing_clauses:")
    if not report.missing_clauses:
        lines.append("  (none)")
    for m in report.missing_clauses:
        lines.append(f"  - {m.clause_name}: {m.recommendation}")

    lines.append("action_items:")
    if not report.action_items:
        lines.append("  (none)")
    for a in report.action_items:
        lines.append(f"  - [{a.priority}] {a.text}")

    return "\n".join(lines)


def _call_gemini_text(api_key: str, prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_ANALYSIS_MODEL)
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2},
        )
    except Exception as exc:
        logger.exception("Gemini text call failed")
        raise AnalysisError(
            "Gemini Q&A request failed. Check GEMINI_API_KEY and model access."
        ) from exc

    return (getattr(response, "text", None) or "").strip()
