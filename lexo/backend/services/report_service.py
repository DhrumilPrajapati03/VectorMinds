"""Fetch persisted reports scoped to the document owner (TKT-017)."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from models.schemas import (
    REPORT_DISCLAIMER,
    ActionItemOut,
    Citation as CitationOut,
    Flag as FlagOut,
    MissingClauseItem,
    ReportRead,
)
from models.tables import (
    ActionItem,
    Citation,
    Document,
    Flag,
    MissingClause,
    Report,
    User,
)

logger = logging.getLogger(__name__)


def get_report(session: Session, user: User, report_id: UUID) -> ReportRead:
    """Return full report JSON; cross-user → 404 (not 403)."""
    report = session.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    doc = session.get(Document, report.document_id)
    if doc is None or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Report not found")

    return _to_read(session, report)


def _to_read(session: Session, report: Report) -> ReportRead:
    flag_rows = session.exec(
        select(Flag).where(Flag.report_id == report.id)
    ).all()
    flags_out: list[FlagOut] = []
    for flag in flag_rows:
        cites = session.exec(
            select(Citation).where(Citation.flag_id == flag.id)
        ).all()
        flags_out.append(
            FlagOut(
                clause_ref=flag.clause_ref,
                issue=flag.issue,
                severity=flag.severity,
                category=flag.category,
                citations=[
                    CitationOut(
                        source_title=c.source_title,
                        source_url=c.source_url,
                        source_snippet=c.source_snippet,
                        verified=c.verified,
                    )
                    for c in cites
                ],
            )
        )

    missing = session.exec(
        select(MissingClause).where(MissingClause.report_id == report.id)
    ).all()
    actions = session.exec(
        select(ActionItem).where(ActionItem.report_id == report.id)
    ).all()

    risk = (report.risk_score or "").strip().lower()
    if risk not in ("green", "yellow", "red"):
        risk = "yellow"

    return ReportRead(
        id=report.id,
        document_id=report.document_id,
        risk_score=risk,  # type: ignore[arg-type]
        summary=report.summary,
        flags=flags_out,
        missing_clauses=[
            MissingClauseItem(
                clause_name=m.clause_name,
                recommendation=m.recommendation,
            )
            for m in missing
        ],
        action_items=[
            ActionItemOut(text=a.text, priority=a.priority) for a in actions
        ],
        disclaimer=REPORT_DISCLAIMER,
        created_at=report.created_at,
    )
