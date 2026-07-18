from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import get_session
from models.schemas import ReportRead
from models.tables import User
from services import report_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_id}", response_model=ReportRead)
async def get_report(
    report_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return report_service.get_report(session, current_user, report_id)
