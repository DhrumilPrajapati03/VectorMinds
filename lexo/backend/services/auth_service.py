"""Auth helpers: password hashing, JWT issuance, signup/login against Neon."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from config import settings
from models.schemas import LoginRequest, SignupRequest, TokenResponse
from models.tables import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _name_from_email(email: str) -> str:
    local = email.split("@", 1)[0].strip()
    return local or email


def _token_for_user(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        user_id=user.id,
        email=user.email,
    )


def signup(session: Session, payload: SignupRequest) -> TokenResponse:
    email = _normalize_email(payload.email)
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    existing = session.exec(select(User).where(User.email == email)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        name=_name_from_email(email),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered") from None

    session.refresh(user)
    logger.info("user_signed_up user_id=%s", user.id)
    return _token_for_user(user)


def login(session: Session, payload: LoginRequest) -> TokenResponse:
    email = _normalize_email(payload.email)
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info("user_logged_in user_id=%s", user.id)
    return _token_for_user(user)
