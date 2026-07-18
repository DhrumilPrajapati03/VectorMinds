from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import get_session
from models.schemas import DocumentRead
from models.tables import User
from services import document_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentRead])
async def list_documents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return document_service.list_documents(session, current_user)


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return document_service.get_document(session, current_user, document_id)
