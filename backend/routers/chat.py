from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from models.chat import ChatSession, ChatMessage, RiskAlert, SessionStatus, RiskLevel, CrisisLevel
from schemas.chat import ChatMessageCreate
from utils.deps import get_current_user, require_role
from utils.ai_service import (
    chat_reply, generate_summary, generate_assessment,
    check_info_complete, is_meaningless_chat, is_repeated_venting, user_wants_to_end,
    ENDING_TEMPLATE, ENDING_EARLY_A_TEMPLATE, ENDING_EARLY_B_TEMPLATE,
    ENDING_EARLY_C_TEMPLATE, ENDING_EARLY_D_TEMPLATE,
)
from utils.risk_analyzer import (
    analyze_risk, _detect_crisis, check_misjudge_cancel, get_crisis_script,
    CRISIS_MISJUDGE_SCRIPT, CRISIS_REFUSE_HUMAN_SCRIPT,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

MAX_FREE_MESSAGES = 10


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
        "is_crisis_mode": s.is_crisis_mode,
        "crisis_level": s.crisis_level.value if s.crisis_level else None,
        "user_message_count": s.user_message_count,
        "ending_reason": s.ending_reason,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def _serialize_alert(a: RiskAlert):
    return {
        "id": a.id,
        "session_id": a.session_id,
        "visitor_id": a.visitor_id,
        "level": a.level.value if a.level else "none",
        "crisis_level": a.crisis_level.value if a.crisis_level else None,
        "summary": a.summary,
        "is_read": a.is_read,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _get_history_dicts(db: Session, session_id: int) -> list[dict]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in messages]


def _end_session_and_summarize(session: ChatSession, db: Session, ending_reason: str):
    messages = _get_history_dicts(db, session.id)
    risk_result = analyze_risk(" ".join([m["content"] for m in messages[-5:]]))
    summary = generate_summary(messages)

    session.status = SessionStatus.COMPLETED
    session.risk_level = risk_result["risk_level"]
    session.risk_summary = risk_result["summary"]
    session.ai_summary = summary
    session.ending_reason = ending_reason

    if risk_result["risk_level"] != RiskLevel.NONE:
        alert = RiskAlert(
            session_id=session.id,
            counselor_id=session.counselor_id or 0,
            visitor_id=session.visitor_id,
            level=risk_result["risk_level"],
            crisis_level=risk_result.get("crisis_level"),
            summary=risk_result["summary"],
        )
        db.add(alert)
        session.alert_sent = True

    db.commit()
    db.refresh(session)


def _create_crisis_alert(session: ChatSession, risk_result: dict, db: Session):
    alert = RiskAlert(
        session_id=session.id,
        counselor_id=session.counselor_id or 0,
        visitor_id=session.visitor_id,
        level=risk_result["risk_level"],
        crisis_level=risk_result["crisis_level"],
        summary=risk_result["summary"],
    )
    db.add(alert)
    session.alert_sent = True


# ==================== 来访者：会话管理 ====================

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

    history_dicts = _get_history_dicts(db, session_id)
    user_text = data.content

    crisis_result = _detect_crisis(user_text)

    if crisis_result["is_crisis"]:
        return _handle_crisis_message(
            session, crisis_result, history_dicts, user_text, db
        )

    if session.is_crisis_mode:
        if check_misjudge_cancel(user_text):
            session.is_crisis_mode = False
            session.crisis_level = None
            db.commit()
            ai_content = CRISIS_MISJUDGE_SCRIPT
            ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
            db.add(ai_msg)
            db.commit()
            db.refresh(ai_msg)
            return {**_serialize_msg(ai_msg), "crisis_cancelled": True}

        ai_content = chat_reply(history_dicts, crisis_mode=True)
        ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)
        return _serialize_msg(ai_msg)

    session.user_message_count = (session.user_message_count or 0) + 1
    db.commit()

    ending_result = _check_early_ending(session, history_dicts, user_text, db)
    if ending_result:
        return ending_result

    ai_content = chat_reply(history_dicts)
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    session.user_message_count = (session.user_message_count or 0)
    db.commit()

    if session.user_message_count >= MAX_FREE_MESSAGES:
        return _handle_level1_ending(session, db)

    return _serialize_msg(ai_msg)


def _handle_crisis_message(
    session: ChatSession, crisis_result: dict, history_dicts: list[dict],
    user_text: str, db: Session
):
    session_id = session.id

    if not session.is_crisis_mode:
        session.is_crisis_mode = True
        session.crisis_level = crisis_result["crisis_level"]
        _create_crisis_alert(session, crisis_result, db)
        db.commit()

        crisis_script = get_crisis_script(crisis_result["crisis_level"])
        ai_natural = chat_reply(history_dicts, crisis_mode=True)
        ai_content = crisis_script + "\n\n" + ai_natural
    else:
        ai_content = chat_reply(history_dicts, crisis_mode=True)

    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        **_serialize_msg(ai_msg),
        "crisis_alert": True,
        "crisis_level": crisis_result["crisis_level"].value,
    }


def _check_early_ending(
    session: ChatSession, history_dicts: list[dict], user_text: str, db: Session
) -> dict | None:

    if user_wants_to_end(user_text):
        ai_content = ENDING_EARLY_D_TEMPLATE
        ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
        db.add(ai_msg)
        _end_session_and_summarize(session, db, "user_wants_end")
        return {**_serialize_msg(ai_msg), "session_ended": True, "ending_reason": "user_wants_end"}

    user_messages = [m for m in history_dicts if m["role"] == "user"]
    count = len(user_messages)

    if count >= 2 and is_meaningless_chat(history_dicts):
        ai_content = ENDING_EARLY_B_TEMPLATE
        ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
        db.add(ai_msg)
        _end_session_and_summarize(session, db, "meaningless_chat")
        return {**_serialize_msg(ai_msg), "session_ended": True, "ending_reason": "meaningless_chat"}

    if count >= 3 and is_repeated_venting(history_dicts):
        ai_content = ENDING_EARLY_C_TEMPLATE
        ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
        db.add(ai_msg)
        _end_session_and_summarize(session, db, "repeated_venting")
        return {**_serialize_msg(ai_msg), "session_ended": True, "ending_reason": "repeated_venting"}

    if count >= 4:
        info = check_info_complete(history_dicts)
        if info.get("all_complete") and not info.get("has_new_question"):
            ai_content = ENDING_EARLY_A_TEMPLATE
            ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
            db.add(ai_msg)
            _end_session_and_summarize(session, db, "info_complete")
            return {**_serialize_msg(ai_msg), "session_ended": True, "ending_reason": "info_complete"}

    return None


def _handle_level1_ending(session: ChatSession, db: Session) -> dict:
    history_dicts = _get_history_dicts(db, session.id)
    assessment = generate_assessment(history_dicts)
    ai_content = ENDING_TEMPLATE.format(assessment=assessment)

    ai_msg = ChatMessage(session_id=session.id, role="assistant", content=ai_content)
    db.add(ai_msg)
    _end_session_and_summarize(session, db, "free_limit_reached")
    return {**_serialize_msg(ai_msg), "session_ended": True, "ending_reason": "free_limit_reached"}


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

    history_dicts = _get_history_dicts(db, session_id)
    assessment = generate_assessment(history_dicts)
    ai_content = ENDING_TEMPLATE.format(assessment=assessment)
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
    db.add(ai_msg)
    _end_session_and_summarize(session, db, "manual_end")
    return _serialize_session(session)


# ==================== 通用：查看会话/消息 ====================

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


# ==================== 咨询师：查看预警 ====================

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