import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Boolean, func
from database import Base


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class RiskLevel(str, enum.Enum):
    NONE = "none"
    YELLOW = "yellow"
    RED = "red"


class CrisisLevel(str, enum.Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.NONE)
    risk_summary = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    alert_sent = Column(Boolean, default=False)
    user_message_count = Column(Integer, default=0)
    is_crisis_mode = Column(Boolean, default=False)
    crisis_level = Column(Enum(CrisisLevel), nullable=True)
    ending_reason = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    level = Column(Enum(RiskLevel), nullable=False)
    crisis_level = Column(Enum(CrisisLevel), nullable=True)
    summary = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())