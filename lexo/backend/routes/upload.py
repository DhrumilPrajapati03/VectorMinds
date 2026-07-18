from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from db import get_session
from models.schemas import UploadResponse
from models.tables import User
from services import document_service
from services.auth_service import get_current_user

router = APIRouter(tags=["upload"])


@router.post("/api/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    data = await file.read()
    return document_service.create_document(
        session, current_user, file, doc_type.strip().lower(), data
    )
