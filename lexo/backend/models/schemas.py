from datetime import datetime
from typing import Literal, Optional
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


class MissingClauseItem(BaseModel):
    """Matches MissingClause table fields used by analysis (TKT-015)."""

    clause_name: str
    recommendation: str


class ActionItemOut(BaseModel):
    """Matches ActionItem table fields used by analysis (TKT-015)."""

    text: str
    priority: str  # high | medium | low


class ClauseSegment(BaseModel):
    """Typed clause from Gemini segmentation (fixed taxonomy per doc_type)."""

    clause_type: str
    text: str
    clause_ref: str = ""


class AnalysisResult(BaseModel):
    """Return type of services.llm.analyze_document (not yet a persisted Report)."""

    summary: str
    risk_score: Literal["green", "yellow", "red"]
    flags: list[Flag]
    missing_clauses: list[MissingClauseItem]
    action_items: list[ActionItemOut]
    clauses: list[ClauseSegment] = Field(default_factory=list)


class SignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UploadResponse(BaseModel):
    document_id: UUID


class DocumentRead(BaseModel):
    id: UUID
    filename: str
    doc_type: str
    mime_type: str
    status: str
    risk_score: Optional[str] = None
    report_id: Optional[UUID] = None
    created_at: datetime


class AnalyzeStartResponse(BaseModel):
    """Immediate response from POST /api/analyze/{document_id}."""

    document_id: UUID
    status: str


# Shown on every report response (TKT-017 / TKT-021 backend field).
REPORT_DISCLAIMER = (
    "This is not legal advice. Lexo is an informational tool only; "
    "consult a qualified lawyer for advice about your situation."
)


class ReportRead(BaseModel):
    """Full persisted report returned by GET /api/reports/{id}."""

    id: UUID
    document_id: UUID
    risk_score: Literal["green", "yellow", "red"]
    summary: str
    flags: list[Flag]
    missing_clauses: list[MissingClauseItem]
    action_items: list[ActionItemOut]
    disclaimer: str = REPORT_DISCLAIMER
    created_at: datetime


class SpeakRequest(BaseModel):
    """Text to convert to speech (typically a report summary)."""

    text: str = Field(min_length=1, max_length=5000)


class AskRequest(BaseModel):
    """Text follow-up question grounded in an existing report (TKT-030)."""

    report_id: UUID
    question: str = Field(min_length=1, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    disclaimer: str = REPORT_DISCLAIMER
