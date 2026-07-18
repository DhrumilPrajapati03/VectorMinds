from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session

from db import get_session
from models.schemas import AskRequest, AskResponse, REPORT_DISCLAIMER, SpeakRequest
from models.tables import User
from services import report_service
from services.auth_service import get_current_user
from services.llm import AnalysisError, answer_question
from services.voice import synthesize_speech

router = APIRouter(tags=["voice"])

_TRANSCRIBE_DETAIL = (
    "Server-side STT is not supported. Use the browser Web Speech API "
    "(SpeechRecognition / webkitSpeechRecognition) on the frontend; "
    "send the text transcript to POST /api/voice/ask. Wispr is not used."
)


@router.post("/api/voice/transcribe")
async def transcribe():
    """Unsupported — STT is client-side Web Speech (TKT-027 / TKT-029)."""
    return JSONResponse(status_code=501, content={"detail": _TRANSCRIBE_DETAIL})


@router.post("/api/voice/speak")
async def speak(
    payload: SpeakRequest,
    current_user: User = Depends(get_current_user),
):
    """ElevenLabs TTS — returns audio/mpeg bytes (TKT-028)."""
    _ = current_user  # auth only; TTS is not user-scoped beyond JWT
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text must not be empty")
    audio = await synthesize_speech(text)
    return Response(content=audio, media_type="audio/mpeg")


@router.post("/api/voice/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Grounded Q&A over an owned report — text question only (TKT-030)."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")
    report = report_service.get_report(session, current_user, payload.report_id)
    try:
        answer = answer_question(report, question)
    except AnalysisError as exc:
        msg = str(exc)
        if "GEMINI_API_KEY" in msg:
            raise HTTPException(status_code=503, detail=msg) from exc
        raise HTTPException(status_code=502, detail=msg) from exc
    return AskResponse(answer=answer, disclaimer=REPORT_DISCLAIMER)
