import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from models.user import User, UserRole, AccountStatus
from models.appointment import Appointment, AppointmentStatus
from models.chat import ChatSession, ChatMessage, RiskAlert, SessionStatus, RiskLevel
from models.assessment import Assessment, Scale, ScaleAssignment, AssignStatus
from utils.deps import get_current_user, require_role

router = APIRouter(prefix="/api/counselor", tags=["counselor"])


def _get_associated_visitor_ids(counselor_id: int, db: Session) -> set[int]:
    """获取与咨询师有关联的来访者ID集合"""
    ids: set[int] = set()
    for row in db.query(Appointment.visitor_id).filter(Appointment.counselor_id == counselor_id).all():
        ids.add(row[0])
    for row in db.query(ChatSession.visitor_id).filter(ChatSession.counselor_id == counselor_id).all():
        ids.add(row[0])
    for row in db.query(ScaleAssignment.visitor_id).filter(ScaleAssignment.counselor_id == counselor_id).all():
        ids.add(row[0])
    for row in db.query(RiskAlert.visitor_id).filter(RiskAlert.counselor_id == counselor_id).all():
        ids.add(row[0])
    return ids


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    cid = current_user.id
    visitor_ids = _get_associated_visitor_ids(cid, db)

    upcoming = (
        db.query(Appointment)
        .filter(Appointment.counselor_id == cid, Appointment.status == AppointmentStatus.PENDING)
        .count()
    )

    unread_alerts = (
        db.query(RiskAlert)
        .filter(RiskAlert.counselor_id == cid, RiskAlert.is_read == False)
        .count()
    )

    total_visitors = len(visitor_ids)

    total_chat_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.counselor_id == cid, ChatSession.status == SessionStatus.COMPLETED)
        .count()
    )

    recent_sessions = (
        db.query(ChatSession)
        .filter(ChatSession.counselor_id == cid, ChatSession.status == SessionStatus.COMPLETED)
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
    q = db.query(ChatSession).filter(ChatSession.counselor_id == current_user.id)
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
    visitor_ids = _get_associated_visitor_ids(current_user.id, db)
    if not visitor_ids:
        return []
    visitors = (
        db.query(User)
        .filter(User.id.in_(visitor_ids), User.status == AccountStatus.ACTIVE)
        .all()
    )
    result = []
    for v in visitors:
        chat_count = db.query(ChatSession).filter(ChatSession.visitor_id == v.id, ChatSession.counselor_id == current_user.id).count()
        assessment_count = db.query(Assessment).filter(Assessment.visitor_id == v.id).count()
        result.append({
            "id": v.id,
            "display_name": v.display_name,
            "chat_count": chat_count,
            "assessment_count": assessment_count,
        })
    return result


def _assert_visitor_associated(visitor_id: int, counselor_id: int, db: Session):
    """校验该来访者是否与当前咨询师有关联"""
    if visitor_id not in _get_associated_visitor_ids(counselor_id, db):
        raise HTTPException(status_code=403, detail="无权查看该来访者的信息")


@router.get("/visitors/{visitor_id}/assessments")
def get_visitor_assessments(
    visitor_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    _assert_visitor_associated(visitor_id, current_user.id, db)
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
    _assert_visitor_associated(visitor_id, current_user.id, db)
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


# ==================== 咨询师分发量表 ====================


@router.get("/scales")
def list_all_scales(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    scales = db.query(Scale).filter(Scale.is_active == 1).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "question_count": len(json.loads(s.questions_json)),
        }
        for s in scales
    ]


@router.get("/scale-assignments")
def list_assignments(
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    assignments = (
        db.query(ScaleAssignment, Scale.name, User.display_name)
        .join(Scale, ScaleAssignment.scale_id == Scale.id)
        .join(User, ScaleAssignment.visitor_id == User.id)
        .filter(ScaleAssignment.counselor_id == current_user.id)
        .order_by(ScaleAssignment.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "visitor_id": a.visitor_id,
            "visitor_name": display_name,
            "scale_id": a.scale_id,
            "scale_name": scale_name,
            "status": a.status.value if a.status else "pending",
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a, scale_name, display_name in assignments
    ]


@router.post("/scale-assignments")
def create_assignment(
    visitor_id: int,
    scale_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    visitor = db.query(User).filter(
        User.id == visitor_id,
        User.role == UserRole.VISITOR,
        User.status == AccountStatus.ACTIVE,
    ).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="来访者不存在")

    scale = db.query(Scale).filter(Scale.id == scale_id, Scale.is_active == 1).first()
    if not scale:
        raise HTTPException(status_code=404, detail="量表不存在")

    existing = (
        db.query(ScaleAssignment)
        .filter(
            ScaleAssignment.counselor_id == current_user.id,
            ScaleAssignment.visitor_id == visitor_id,
            ScaleAssignment.scale_id == scale_id,
            ScaleAssignment.status == AssignStatus.PENDING,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="该量表已分配给此来访者，请勿重复分配")

    done = (
        db.query(Assessment)
        .filter(
            Assessment.visitor_id == visitor_id,
            Assessment.scale_id == scale_id,
        )
        .first()
    )
    if done:
        raise HTTPException(status_code=409, detail="该来访者已完成此量表")

    assignment = ScaleAssignment(
        counselor_id=current_user.id,
        visitor_id=visitor_id,
        scale_id=scale_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {
        "id": assignment.id,
        "visitor_id": visitor_id,
        "scale_id": scale_id,
        "status": "pending",
    }


@router.delete("/scale-assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(ScaleAssignment)
        .filter(
            ScaleAssignment.id == assignment_id,
            ScaleAssignment.counselor_id == current_user.id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="分配记录不存在")
    db.delete(assignment)
    db.commit()
    return {"ok": True}