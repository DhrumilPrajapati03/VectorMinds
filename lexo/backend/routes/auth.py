from fastapi import APIRouter, Depends
from sqlmodel import Session

from db import get_session
from models.schemas import LoginRequest, SignupRequest, TokenResponse
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: SignupRequest, session: Session = Depends(get_session)):
    return auth_service.signup(session, payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: Session = Depends(get_session)):
    return auth_service.login(session, payload)
