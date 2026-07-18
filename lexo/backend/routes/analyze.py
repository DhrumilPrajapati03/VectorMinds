from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session

from db import get_session
from models.schemas import AnalyzeStartResponse
from models.tables import User
from services import analyze_service
from services.rate_limit import enforce_analyze_rate_limit

router = APIRouter(tags=["analyze"])


@router.post(
    "/api/analyze/{document_id}",
    response_model=AnalyzeStartResponse,
)
async def analyze(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(enforce_analyze_rate_limit),
):
    return analyze_service.start_analyze(
        session, current_user, document_id, background_tasks
    )
