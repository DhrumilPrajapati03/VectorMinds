from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_title: str
    source_url: str
    source_snippet: str
    verified: bool


class Flag(BaseModel):
    clause_ref: str
    issue: str
    severity: str
    category: str
    citations: list[Citation]


class Report(BaseModel):
    document_id: UUID
    risk_score: str  # green | yellow | red
    summary: str
    created_at: datetime
    flags: list[Flag]
    missing_clauses: list[str]
    action_items: list[str]


class SignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
