from pydantic import BaseModel


class Flag(BaseModel):
    clause: str
    issue: str
    citation: str
    severity: str


class Report(BaseModel):
    risk_score: str  # green | yellow | red
    flags: list[Flag]
    missing_clauses: list[str]
    action_items: list[str]
