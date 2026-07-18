"""Lean Exa grounding for analysis flags (TKT-023).

SPEED CAPS (hackathon):
- Ground at most MAX_FLAGS_TO_GROUND flags (highest severity first).
- Skip missing_clauses entirely for MVP (no Exa calls for them).

Never fabricates statute URLs. On missing key / Exa errors / no trusted hit,
returns an explicit unverified citation.
"""

from __future__ import annotations

import logging
from urllib.parse import urlparse

import httpx

from models.schemas import Citation, Flag

logger = logging.getLogger(__name__)

# Trusted domains only — keep this list short.
TRUSTED_EXACT_HOSTS = frozenset(
    {
        "indiacode.nic.in",
        "www.indiacode.nic.in",
        "indiankanoon.org",
        "www.indiankanoon.org",
    }
)
TRUSTED_SUFFIXES = (".gov.in", ".nic.in")
MINISTRY_HINTS = ("ministry", "labour", "legalaffairs", "indiacode")

# Prefer these domains in the Exa request (API includeDomains).
EXA_INCLUDE_DOMAINS = ["indiacode.nic.in", "indiankanoon.org"]

EXA_SEARCH_URL = "https://api.exa.ai/search"
MAX_FLAGS_TO_GROUND = 3  # SPEED CAP — do not raise without a good reason
# missing_clauses: skipped for MVP (no grounding calls).

SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}

UNVERIFIED_TITLE = "Unverified / general principle"


def unverified_citation() -> Citation:
    """Explicit unverified placeholder — never invent a fake law URL."""
    return Citation(
        source_title=UNVERIFIED_TITLE,
        source_url="",
        source_snippet="",
        verified=False,
    )


def _hostname(url: str) -> str:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return ""
    return host


def is_trusted_url(url: str) -> bool:
    """True only for indiacode / indiankanoon / *.gov.in / ministry-looking .in hosts."""
    host = _hostname(url)
    if not host:
        return False
    if host in TRUSTED_EXACT_HOSTS:
        return True
    if any(host.endswith(suffix) for suffix in TRUSTED_SUFFIXES):
        return True
    if host.endswith(".in") and any(hint in host for hint in MINISTRY_HINTS):
        return True
    return False


def find_citation(query: str) -> Citation:
    """Search Exa for a trusted-domain citation, or return unverified."""
    q = (query or "").strip()
    if not q:
        return unverified_citation()

    from config import settings

    api_key = (settings.exa_api_key or "").strip()
    if not api_key:
        logger.info("exa_grounding skipped: EXA_API_KEY not set")
        return unverified_citation()

    payload = {
        "query": q,
        "type": "fast",
        "numResults": 5,
        "includeDomains": EXA_INCLUDE_DOMAINS,
        "contents": {
            "highlights": True,
            "text": {"maxCharacters": 400},
        },
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(
                EXA_SEARCH_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                },
                json=payload,
            )
            if resp.status_code != 200:
                logger.info(
                    "exa_search_non_200 status=%s",
                    resp.status_code,
                )
                return unverified_citation()
            data = resp.json()
    except Exception:
        logger.exception("exa_search_failed")
        return unverified_citation()

    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return unverified_citation()

    for item in results:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or "").strip()
        if not url or not is_trusted_url(url):
            continue
        title = (item.get("title") or "").strip() or "Legal source"
        snippet = _snippet_from_result(item)
        return Citation(
            source_title=title[:500],
            source_url=url,
            source_snippet=snippet[:1000],
            verified=True,
        )

    logger.info("exa_grounding no trusted hit for query_len=%s", len(q))
    return unverified_citation()


def _snippet_from_result(item: dict) -> str:
    highlights = item.get("highlights")
    if isinstance(highlights, list) and highlights:
        parts = [str(h).strip() for h in highlights if str(h).strip()]
        if parts:
            return " ".join(parts)[:1000]
    text = item.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()[:1000]
    return ""


def ground_flags(flags: list[Flag]) -> list[Flag]:
    """Attach citations to flags. At most MAX_FLAGS_TO_GROUND get an Exa call.

    Remaining flags get an unverified citation (no Exa call) so the report
    always surfaces verified/unverified clearly. missing_clauses are not grounded.
    """
    if not flags:
        return []

    ranked = sorted(
        range(len(flags)),
        key=lambda i: SEVERITY_RANK.get((flags[i].severity or "").lower(), 9),
    )
    to_ground = set(ranked[:MAX_FLAGS_TO_GROUND])

    out: list[Flag] = []
    for i, flag in enumerate(flags):
        if i in to_ground:
            query = (
                f"India law {flag.category} {flag.issue} "
                f"site:indiacode.nic.in OR site:indiankanoon.org"
            )
            citation = find_citation(query)
        else:
            citation = unverified_citation()
        out.append(flag.model_copy(update={"citations": [citation]}))

    grounded = sum(1 for i in to_ground)
    logger.info(
        "ground_flags done flags=%s exa_attempts=%s",
        len(flags),
        grounded,
    )
    return out
