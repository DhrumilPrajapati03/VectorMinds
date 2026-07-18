from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from db import get_session
from models.schemas import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)
from models.tables import User
from services import auth_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: SignupRequest, session: Session = Depends(get_session)):
    return auth_service.signup(session, payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: Session = Depends(get_session)):
    return auth_service.login(session, payload)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest, session: Session = Depends(get_session)):
    return auth_service.refresh(session, payload)


@router.post("/logout", status_code=204)
async def logout(
    payload: LogoutRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    auth_service.logout(session, payload, current_user)
    return Response(status_code=204)
