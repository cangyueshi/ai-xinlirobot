from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    content: str


class ChatSessionResponse(BaseModel):
    id: int
    visitor_id: int
    counselor_id: int | None = None
    status: str
    risk_level: str
    risk_summary: str | None = None
    ai_summary: str | None = None
    alert_sent: bool
    created_at: str | None = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: str | None = None


class RiskAlertResponse(BaseModel):
    id: int
    session_id: int
    visitor_id: int
    level: str
    summary: str
    is_read: bool
    created_at: str | None = None