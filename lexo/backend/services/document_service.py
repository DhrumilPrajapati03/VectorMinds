"""Document create/list/get — always scoped to the authenticated user."""

from __future__ import annotations

import logging
import re
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, col, select

from models.schemas import DocumentRead, UploadResponse
from models.tables import (
    ActionItem,
    Citation,
    Document,
    Flag,
    MissingClause,
    Report,
    User,
)
from services import storage

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_DOC_TYPES = frozenset({"rental", "employment"})
ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _safe_filename(name: str) -> str:
    base = (name or "upload").replace("\\", "/").split("/")[-1].strip()
    base = re.sub(r"[^\w.\-]+", "_", base)
    return base[:200] or "upload"


def _validate_upload(file: UploadFile, doc_type: str, data: bytes) -> tuple[str, str]:
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail="doc_type must be 'rental' or 'employment'",
        )

    filename = _safe_filename(file.filename or "")
    lower = filename.lower()
    ext = None
    for candidate in ALLOWED_EXTENSIONS:
        if lower.endswith(candidate):
            ext = candidate
            break
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF and DOCX are allowed.",
        )

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB.",
        )

    mime_type = ALLOWED_EXTENSIONS[ext]
    return filename, mime_type


def create_document(
    session: Session,
    user: User,
    file: UploadFile,
    doc_type: str,
    data: bytes,
) -> UploadResponse:
    filename, mime_type = _validate_upload(file, doc_type, data)
    document_id = uuid4()
    storage_key = f"{user.id}/{document_id}/{filename}"

    try:
        storage.upload_file(data, storage_key)
    except ValueError as exc:
        logger.exception("upload_storage_rejected user_id=%s", user.id)
        raise HTTPException(status_code=400, detail="Invalid storage key") from exc
    except OSError:
        logger.exception("upload_storage_failed user_id=%s", user.id)
        raise HTTPException(status_code=500, detail="Failed to store file") from None

    doc = Document(
        id=document_id,
        user_id=user.id,
        filename=filename,
        storage_key=storage_key,
        doc_type=doc_type,
        mime_type=mime_type,
        status="uploaded",
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    logger.info("document_uploaded document_id=%s user_id=%s", doc.id, user.id)
    return UploadResponse(document_id=doc.id)


def _report_for(session: Session, document_id: UUID) -> Report | None:
    return session.exec(
        select(Report).where(Report.document_id == document_id)
    ).first()


def _to_read(session: Session, doc: Document) -> DocumentRead:
    report = _report_for(session, doc.id)
    return DocumentRead(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type,
        mime_type=doc.mime_type,
        status=doc.status,
        risk_score=report.risk_score if report is not None else None,
        report_id=report.id if report is not None else None,
        created_at=doc.created_at,
    )


def list_documents(session: Session, user: User) -> list[DocumentRead]:
    docs = session.exec(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(col(Document.created_at).desc())
    ).all()
    return [_to_read(session, d) for d in docs]


def get_document(session: Session, user: User, document_id: UUID) -> DocumentRead:
    doc = session.exec(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id,
        )
    ).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return _to_read(session, doc)


def delete_document(session: Session, user: User, document_id: UUID) -> None:
    """Delete owned document + cascade report children + local blob (TKT-037).

    Cross-user → 404. Missing blob is ignored cleanly.
    """
    doc = session.exec(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id,
        )
    ).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    storage_key = doc.storage_key
    report = _report_for(session, doc.id)
    if report is not None:
        flags = session.exec(select(Flag).where(Flag.report_id == report.id)).all()
        for flag in flags:
            cites = session.exec(
                select(Citation).where(Citation.flag_id == flag.id)
            ).all()
            for cite in cites:
                session.delete(cite)
            session.delete(flag)

        for missing in session.exec(
            select(MissingClause).where(MissingClause.report_id == report.id)
        ).all():
            session.delete(missing)

        for action in session.exec(
            select(ActionItem).where(ActionItem.report_id == report.id)
        ).all():
            session.delete(action)

        session.delete(report)

    session.delete(doc)
    session.commit()

    try:
        storage.delete_file(storage_key)
    except FileNotFoundError:
        logger.info(
            "document_blob_already_gone document_id=%s key=%s",
            document_id,
            storage_key,
        )
    except ValueError:
        logger.info(
            "document_blob_skip_invalid_key document_id=%s",
            document_id,
        )

    logger.info("document_deleted document_id=%s user_id=%s", document_id, user.id)
