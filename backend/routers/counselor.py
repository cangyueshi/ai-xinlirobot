import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from models.user import User, UserRole
from models.appointment import Appointment, AppointmentStatus
from models.chat import ChatSession, ChatMessage, RiskAlert, SessionStatus, RiskLevel
from models.assessment import Assessment, Scale
from utils.deps import get_current_user, require_role

router = APIRouter(prefix="/api/counselor", tags=["counselor"])


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    upcoming = (
        db.query(Appointment)
        .filter(
            Appointment.counselor_id == current_user.id,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .count()
    )

    unread_alerts = (
        db.query(RiskAlert)
        .filter(RiskAlert.is_read == False)
        .count()
    )

    total_visitors = (
        db.query(User)
        .filter(User.role == UserRole.VISITOR, User.is_active == True)
        .count()
    )

    total_chat_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.status == SessionStatus.COMPLETED)
        .count()
    )

    recent_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.status == SessionStatus.COMPLETED)
        .order_by(ChatSession.updated_at.desc())
        .limit(3)
        .all()
    )

    return {
        "upcoming_appointments": upcoming,
        "unread_alerts": unread_alerts,
        "total_visitors": total_visitors,
        "total_chat_sessions": total_chat_sessions,
        "recent_sessions": [
            {
                "id": s.id,
                "visitor_id": s.visitor_id,
                "risk_level": s.risk_level.value if s.risk_level else "none",
                "ai_summary": s.ai_summary,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in recent_sessions
        ],
    }


@router.get("/sessions")
def get_all_sessions(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
    risk: str | None = None,
):
    q = db.query(ChatSession)
    if risk:
        q = q.filter(ChatSession.risk_level == RiskLevel(risk))
    sessions = q.order_by(ChatSession.created_at.desc()).limit(50).all()
    return [
        {
            "id": s.id,
            "visitor_id": s.visitor_id,
            "status": s.status.value if s.status else "active",
            "risk_level": s.risk_level.value if s.risk_level else "none",
            "risk_summary": s.risk_summary,
            "ai_summary": s.ai_summary,
            "alert_sent": s.alert_sent,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


@router.get("/visitors")
def list_all_visitors(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    visitors = (
        db.query(User)
        .filter(User.role == UserRole.VISITOR, User.is_active == True)
        .all()
    )
    result = []
    for v in visitors:
        chat_count = db.query(ChatSession).filter(ChatSession.visitor_id == v.id).count()
        assessment_count = db.query(Assessment).filter(Assessment.visitor_id == v.id).count()
        result.append({
            "id": v.id,
            "display_name": v.display_name,
            "phone": v.phone,
            "chat_count": chat_count,
            "assessment_count": assessment_count,
        })
    return result


@router.get("/visitors/{visitor_id}/assessments")
def get_visitor_assessments(
    visitor_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Assessment, Scale.name)
        .join(Scale, Assessment.scale_id == Scale.id)
        .filter(Assessment.visitor_id == visitor_id)
        .order_by(Assessment.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "scale_name": scale_name,
            "total_score": a.total_score,
            "result_level": a.result_level.value if a.result_level else "none",
            "result_detail": a.result_detail,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a, scale_name in results
    ]


@router.get("/visitors/{visitor_id}/sessions")
def get_visitor_sessions(
    visitor_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.visitor_id == visitor_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "status": s.status.value if s.status else "active",
            "risk_level": s.risk_level.value if s.risk_level else "none",
            "risk_summary": s.risk_summary,
            "ai_summary": s.ai_summary,
            "alert_sent": s.alert_sent,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]