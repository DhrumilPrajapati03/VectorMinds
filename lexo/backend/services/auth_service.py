"""Auth helpers: password hashing, JWT issuance, signup/login/refresh/logout."""

from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from config import settings
from db import get_session
from models.schemas import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
)
from models.tables import RefreshToken, User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _issue_refresh_token(session: Session, user_id: UUID) -> str:
    raw = secrets.token_urlsafe(32)
    row = RefreshToken(
        user_id=user_id,
        token_hash=_hash_refresh_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(row)
    session.commit()
    return raw


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _name_from_email(email: str) -> str:
    local = email.split("@", 1)[0].strip()
    return local or email


def _token_for_user(session: Session, user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=_issue_refresh_token(session, user.id),
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
    return _token_for_user(session, user)


def login(session: Session, payload: LoginRequest) -> TokenResponse:
    email = _normalize_email(payload.email)
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info("user_logged_in user_id=%s", user.id)
    return _token_for_user(session, user)


def _lookup_refresh_row(session: Session, raw_token: str) -> RefreshToken | None:
    token_hash = _hash_refresh_token(raw_token)
    return session.exec(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).first()


def _is_expired(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)


def refresh(session: Session, payload: RefreshRequest) -> AccessTokenResponse:
    row = _lookup_refresh_row(session, payload.refresh_token)
    if row is None or _is_expired(row.expires_at):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = session.get(User, row.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    logger.info("access_token_refreshed user_id=%s", user.id)
    return AccessTokenResponse(access_token=create_access_token(user.id))


def logout(session: Session, payload: LogoutRequest, current_user: User) -> None:
    row = _lookup_refresh_row(session, payload.refresh_token)
    if row is None or row.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    session.delete(row)
    session.commit()
    logger.info("user_logged_out user_id=%s", current_user.id)


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc

    if payload.get("type") not in (None, "access"):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    try:
        return UUID(str(sub))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_access_token(credentials.credentials)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
