"""Analyze pipeline orchestration (TKT-016) + report persistence (TKT-017/024).

Flow: extract → analyze (Gemini) → ground (Exa, best-effort) → persist → analyzed.
Background task opens its own DB session; never reuse the request session.
"""

from __future__ import annotations

import logging
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session, select

from db import engine
from models.schemas import AnalysisResult, AnalyzeStartResponse
from models.tables import (
    ActionItem,
    Citation,
    Document,
    Flag,
    MissingClause,
    Report,
    User,
)
from services import extraction, grounding
from services.extraction import ExtractionError
from services.llm import AnalysisError, analyze_document

logger = logging.getLogger(__name__)

IN_PROGRESS_STATUSES = frozenset({"extracting", "analyzing", "grounding"})
STARTABLE_STATUSES = frozenset({"uploaded", "failed"})


def start_analyze(
    session: Session,
    user: User,
    document_id: UUID,
    background_tasks: BackgroundTasks,
) -> AnalyzeStartResponse:
    """Validate ownership/status, set extracting, enqueue background pipeline."""
    doc = session.exec(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id,
        )
    ).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status in IN_PROGRESS_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Analysis already in progress (status={doc.status})",
        )
    if doc.status == "analyzed":
        raise HTTPException(
            status_code=409,
            detail="Document already analyzed",
        )
    if doc.status not in STARTABLE_STATUSES:
        raise HTTPException(
            status_code=409,
            detail=f"Document cannot be analyzed from status={doc.status}",
        )

    doc.status = "extracting"
    session.add(doc)
    session.commit()
    session.refresh(doc)

    background_tasks.add_task(run_analyze_pipeline, document_id)
    logger.info(
        "analyze_started document_id=%s user_id=%s",
        document_id,
        user.id,
    )
    return AnalyzeStartResponse(document_id=document_id, status="extracting")


def run_analyze_pipeline(document_id: UUID) -> None:
    """Background entrypoint — owns its own Session."""
    with Session(engine) as session:
        try:
            _run_pipeline(session, document_id)
        except Exception:
            logger.exception(
                "analyze_pipeline_unhandled document_id=%s",
                document_id,
            )
            _set_failed(session, document_id)


def _run_pipeline(session: Session, document_id: UUID) -> None:
    doc = session.get(Document, document_id)
    if doc is None:
        logger.info("analyze_pipeline missing document_id=%s", document_id)
        return

    # 1) extracting (already set by start_analyze; refresh for clarity)
    _set_status(session, doc, "extracting")

    try:
        text = extraction.extract_text_from_storage(doc.storage_key, doc.mime_type)
    except ExtractionError:
        logger.exception("extract_failed document_id=%s", document_id)
        _set_failed(session, document_id)
        return
    except Exception:
        logger.exception("extract_unexpected document_id=%s", document_id)
        _set_failed(session, document_id)
        return

    # 2) analyzing
    _set_status(session, doc, "analyzing")
    try:
        analysis = analyze_document(text, doc.doc_type)
    except AnalysisError:
        logger.exception("llm_analyze_failed document_id=%s", document_id)
        _set_failed(session, document_id)
        return
    except Exception:
        logger.exception("llm_analyze_unexpected document_id=%s", document_id)
        _set_failed(session, document_id)
        return

    # 3) grounding (best-effort — Exa unavailable still continues)
    _set_status(session, doc, "grounding")
    try:
        grounded_flags = grounding.ground_flags(analysis.flags)
        analysis = analysis.model_copy(update={"flags": grounded_flags})
    except Exception:
        logger.exception(
            "grounding_failed_continuing document_id=%s",
            document_id,
        )
        # Attach unverified citations so persist still has citation rows.
        fallback = [
            f.model_copy(update={"citations": [grounding.unverified_citation()]})
            for f in analysis.flags
        ]
        analysis = analysis.model_copy(update={"flags": fallback})

    # 4) persist report + children
    try:
        _persist_report(session, doc, analysis)
    except Exception:
        logger.exception("persist_report_failed document_id=%s", document_id)
        _set_failed(session, document_id)
        return

    # 5) done
    _set_status(session, doc, "analyzed")
    logger.info("analyze_complete document_id=%s", document_id)


def _set_status(session: Session, doc: Document, status: str) -> None:
    doc.status = status
    session.add(doc)
    session.commit()
    session.refresh(doc)


def _set_failed(session: Session, document_id: UUID) -> None:
    doc = session.get(Document, document_id)
    if doc is None:
        return
    doc.status = "failed"
    session.add(doc)
    session.commit()


def _persist_report(
    session: Session,
    doc: Document,
    analysis: AnalysisResult,
) -> Report:
    """Write Report + Flag + Citation + MissingClause + ActionItem rows."""
    existing = session.exec(
        select(Report).where(Report.document_id == doc.id)
    ).first()
    if existing is not None:
        # Replace children if a prior failed run left a partial report (unlikely
        # with unique document_id; keep path simple for retries).
        _delete_report_tree(session, existing)
        session.delete(existing)
        session.commit()

    report = Report(
        id=uuid4(),
        document_id=doc.id,
        risk_score=analysis.risk_score,
        summary=analysis.summary,
    )
    session.add(report)
    session.flush()

    for f in analysis.flags:
        flag_row = Flag(
            id=uuid4(),
            report_id=report.id,
            clause_ref=f.clause_ref,
            issue=f.issue,
            severity=f.severity,
            category=f.category,
        )
        session.add(flag_row)
        session.flush()
        for c in f.citations:
            session.add(
                Citation(
                    id=uuid4(),
                    flag_id=flag_row.id,
                    source_title=c.source_title,
                    source_url=c.source_url or "",
                    source_snippet=c.source_snippet or "",
                    verified=bool(c.verified),
                )
            )

    for m in analysis.missing_clauses:
        session.add(
            MissingClause(
                id=uuid4(),
                report_id=report.id,
                clause_name=m.clause_name,
                recommendation=m.recommendation,
            )
        )

    for a in analysis.action_items:
        session.add(
            ActionItem(
                id=uuid4(),
                report_id=report.id,
                text=a.text,
                priority=a.priority,
            )
        )

    session.commit()
    session.refresh(report)
    logger.info(
        "report_persisted report_id=%s document_id=%s flags=%s",
        report.id,
        doc.id,
        len(analysis.flags),
    )
    return report


def _delete_report_tree(session: Session, report: Report) -> None:
    flags = session.exec(select(Flag).where(Flag.report_id == report.id)).all()
    for flag in flags:
        citations = session.exec(
            select(Citation).where(Citation.flag_id == flag.id)
        ).all()
        for c in citations:
            session.delete(c)
        session.delete(flag)
    for m in session.exec(
        select(MissingClause).where(MissingClause.report_id == report.id)
    ).all():
        session.delete(m)
    for a in session.exec(
        select(ActionItem).where(ActionItem.report_id == report.id)
    ).all():
        session.delete(a)
    session.flush()
