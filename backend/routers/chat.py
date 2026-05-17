from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from models.chat import ChatSession, ChatMessage, RiskAlert, SessionStatus, RiskLevel
from schemas.chat import ChatMessageCreate
from utils.deps import get_current_user, require_role
from utils.ai_service import chat_reply, generate_summary
from utils.risk_analyzer import analyze_risk

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _serialize_msg(m: ChatMessage):
    return {
        "id": m.id,
        "session_id": m.session_id,
        "role": m.role,
        "content": m.content,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def _serialize_session(s: ChatSession):
    return {
        "id": s.id,
        "visitor_id": s.visitor_id,
        "counselor_id": s.counselor_id,
        "status": s.status.value if s.status else None,
        "risk_level": s.risk_level.value if s.risk_level else "none",
        "risk_summary": s.risk_summary,
        "ai_summary": s.ai_summary,
        "alert_sent": s.alert_sent,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _serialize_alert(a: RiskAlert):
    return {
        "id": a.id,
        "session_id": a.session_id,
        "visitor_id": a.visitor_id,
        "level": a.level.value if a.level else "none",
        "summary": a.summary,
        "is_read": a.is_read,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# ==================== 来访者：发起对话 / 发送消息 / 结束对话 ====================

@router.post("/sessions")
def create_session(
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(ChatSession)
        .filter(
            ChatSession.visitor_id == current_user.id,
            ChatSession.status == SessionStatus.ACTIVE,
        )
        .first()
    )
    if existing:
        return _serialize_session(existing)

    session = ChatSession(visitor_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return _serialize_session(session)


@router.post("/sessions/{session_id}/message")
def send_message(
    session_id: int,
    data: ChatMessageCreate,
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.visitor_id == current_user.id,
            ChatSession.status == SessionStatus.ACTIVE,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在或已结束")

    user_msg = ChatMessage(session_id=session_id, role="user", content=data.content)
    db.add(user_msg)
    db.commit()

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    ai_content = chat_reply(history_dicts)
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return _serialize_msg(ai_msg)


@router.post("/sessions/{session_id}/end")
def end_session(
    session_id: int,
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.visitor_id == current_user.id,
            ChatSession.status == SessionStatus.ACTIVE,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在或已结束")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]

    risk_result = analyze_risk(msg_dicts)
    summary = generate_summary(msg_dicts)

    session.status = SessionStatus.COMPLETED
    session.risk_level = risk_result["level"]
    session.risk_summary = risk_result["summary"]
    session.ai_summary = summary

    if risk_result["level"] != RiskLevel.NONE:
        alert = RiskAlert(
            session_id=session.id,
            counselor_id=session.counselor_id or 0,
            visitor_id=session.visitor_id,
            level=risk_result["level"],
            summary=risk_result["summary"],
        )
        db.add(alert)
        session.alert_sent = True

    db.commit()
    db.refresh(session)
    return _serialize_session(session)


@router.get("/sessions/mine")
def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(ChatSession)
    if current_user.role == UserRole.VISITOR:
        q = q.filter(ChatSession.visitor_id == current_user.id)
    result = q.order_by(ChatSession.created_at.desc()).all()
    return [_serialize_session(s) for s in result]


@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="对话不存在")

    if current_user.role == UserRole.VISITOR and session.visitor_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [_serialize_msg(m) for m in messages]


# ==================== 咨询师：查看预警 / 查看对话 ====================

@router.get("/alerts")
def get_alerts(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(RiskAlert)
        .filter(
            or_(
                RiskAlert.counselor_id == current_user.id,
                RiskAlert.counselor_id == 0,
            )
        )
        .order_by(RiskAlert.created_at.desc())
        .all()
    )
    return [_serialize_alert(a) for a in alerts]


@router.post("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    alert = (
        db.query(RiskAlert)
        .filter(RiskAlert.id == alert_id, RiskAlert.counselor_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    alert.is_read = True
    db.commit()
    return {"ok": True}


@router.get("/alerts/count")
def alert_count(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    count = (
        db.query(RiskAlert)
        .filter(
            RiskAlert.counselor_id == current_user.id,
            RiskAlert.is_read == False,
        )
        .count()
    )
    return {"unread": count}