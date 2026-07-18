from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=utc_now)


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    filename: str
    storage_key: str
    doc_type: str
    mime_type: str
    page_count: Optional[int] = None
    status: str = Field(default="uploaded", index=True)
    created_at: datetime = Field(default_factory=utc_now)


class Report(SQLModel, table=True):
    __tablename__ = "reports"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="documents.id", unique=True, index=True)
    risk_score: str
    summary: str
    created_at: datetime = Field(default_factory=utc_now)


class Flag(SQLModel, table=True):
    __tablename__ = "flags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    report_id: UUID = Field(foreign_key="reports.id", index=True)
    clause_ref: str
    issue: str
    severity: str
    category: str


class Citation(SQLModel, table=True):
    __tablename__ = "citations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    flag_id: UUID = Field(foreign_key="flags.id", index=True)
    source_title: str
    source_url: str
    source_snippet: str
    verified: bool = False
    retrieved_at: datetime = Field(default_factory=utc_now)


class MissingClause(SQLModel, table=True):
    __tablename__ = "missing_clauses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    report_id: UUID = Field(foreign_key="reports.id", index=True)
    clause_name: str
    recommendation: str


class ActionItem(SQLModel, table=True):
    __tablename__ = "action_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    report_id: UUID = Field(foreign_key="reports.id", index=True)
    text: str
    priority: str


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    token_hash: str
    expires_at: datetime
