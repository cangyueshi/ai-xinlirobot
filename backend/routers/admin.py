import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole, AccountStatus, ExportLog
from models.chat import ChatSession, ChatMessage
from schemas.user import (
    CreateCounselor, UpdateCounselor, CreateSubAdmin, UpdateSubAdmin,
    ResetUserPassword, UserResponse,
)
from utils.security import hash_password
from utils.deps import require_admin, require_super_admin, get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _serialize_user(u: User) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "openid": u.openid,
        "display_name": u.display_name,
        "role": u.role.value if u.role else None,
        "email": u.email,
        "avatar_url": u.avatar_url,
        "bio": u.bio,
        "specialties": u.specialties,
        "status": u.status.value if u.status else None,
        "must_change_password": u.must_change_password,
        "sub_admin_permissions": u.sub_admin_permissions,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


# ==================== 咨询师管理 ====================

@router.post("/counselors")
def create_counselor(
    data: CreateCounselor,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="账号已存在")

    counselor = User(
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=UserRole.COUNSELOR,
        email=data.email,
        bio=data.bio,
        specialties=data.specialties,
        must_change_password=True,
    )
    db.add(counselor)
    db.commit()
    db.refresh(counselor)
    return _serialize_user(counselor)


@router.get("/counselors")
def list_counselors(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    counselors = (
        db.query(User)
        .filter(User.role == UserRole.COUNSELOR, User.status != AccountStatus.DELETED)
        .order_by(User.created_at.desc())
        .all()
    )
    return [_serialize_user(c) for c in counselors]


@router.get("/counselors/{counselor_id}")
def get_counselor(
    counselor_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    return _serialize_user(counselor)


@router.put("/counselors/{counselor_id}")
def update_counselor(
    counselor_id: int,
    data: UpdateCounselor,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    if data.display_name is not None:
        counselor.display_name = data.display_name
    if data.email is not None:
        counselor.email = data.email
    if data.bio is not None:
        counselor.bio = data.bio
    if data.specialties is not None:
        counselor.specialties = data.specialties

    db.commit()
    return _serialize_user(counselor)


@router.post("/counselors/{counselor_id}/reset-password")
def reset_counselor_password(
    counselor_id: int,
    data: ResetUserPassword,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    counselor.password_hash = hash_password(data.new_password)
    counselor.must_change_password = True
    db.commit()
    return {"ok": True, "message": "密码已重置，用户下次登录需修改密码"}


@router.post("/counselors/{counselor_id}/disable")
def disable_counselor(
    counselor_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    counselor.status = AccountStatus.DISABLED
    db.commit()
    return {"ok": True, "message": "账号已禁用"}


@router.post("/counselors/{counselor_id}/enable")
def enable_counselor(
    counselor_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    counselor.status = AccountStatus.ACTIVE
    db.commit()
    return {"ok": True, "message": "账号已启用"}


@router.delete("/counselors/{counselor_id}")
def delete_counselor(
    counselor_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselor = (
        db.query(User)
        .filter(User.id == counselor_id, User.role == UserRole.COUNSELOR)
        .first()
    )
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    counselor.status = AccountStatus.DELETED
    db.commit()
    return {"ok": True, "message": "账号已删除，数据已保留"}


# ==================== 次级管理员管理 ====================

@router.post("/sub-admins")
def create_sub_admin(
    data: CreateSubAdmin,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="账号已存在")

    sub = User(
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=UserRole.SUB_ADMIN,
        email=data.email,
        sub_admin_permissions=data.permissions,
        must_change_password=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return _serialize_user(sub)


@router.get("/sub-admins")
def list_sub_admins(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    subs = (
        db.query(User)
        .filter(User.role == UserRole.SUB_ADMIN, User.status != AccountStatus.DELETED)
        .order_by(User.created_at.desc())
        .all()
    )
    return [_serialize_user(s) for s in subs]


@router.put("/sub-admins/{admin_id}")
def update_sub_admin(
    admin_id: int,
    data: UpdateSubAdmin,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(User)
        .filter(User.id == admin_id, User.role == UserRole.SUB_ADMIN)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="次级管理员不存在")

    if data.display_name is not None:
        sub.display_name = data.display_name
    if data.email is not None:
        sub.email = data.email
    if data.permissions is not None:
        sub.sub_admin_permissions = data.permissions

    db.commit()
    return _serialize_user(sub)


@router.delete("/sub-admins/{admin_id}")
def delete_sub_admin(
    admin_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(User)
        .filter(User.id == admin_id, User.role == UserRole.SUB_ADMIN)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="次级管理员不存在")

    sub.status = AccountStatus.DELETED
    db.commit()
    return {"ok": True, "message": "账号已删除"}


# ==================== 来访者管理 ====================

@router.get("/visitors")
def list_visitors(
    keyword: str = Query(default=""),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(User).filter(User.role == UserRole.VISITOR, User.status != AccountStatus.DELETED)
    if keyword:
        q = q.filter(
            User.display_name.contains(keyword) | User.openid.contains(keyword)
        )
    visitors = q.order_by(User.created_at.desc()).limit(200).all()
    return [_serialize_user(v) for v in visitors]


# ==================== 数据导出 ====================

@router.get("/export/visitors")
def export_visitors(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    visitors = (
        db.query(User)
        .filter(User.role == UserRole.VISITOR)
        .order_by(User.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "昵称", "OpenID", "头像URL", "注册时间", "状态"])
    for v in visitors:
        writer.writerow([
            v.id,
            v.display_name,
            v.openid,
            v.avatar_url,
            v.created_at.isoformat() if v.created_at else "",
            v.status.value if v.status else "",
        ])

    _log_export(current_user, "visitors", db)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=visitors_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/export/counselors")
def export_counselors(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    counselors = (
        db.query(User)
        .filter(User.role == UserRole.COUNSELOR)
        .order_by(User.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "姓名", "账号", "擅长领域", "简介", "状态", "注册时间"])
    for c in counselors:
        writer.writerow([
            c.id,
            c.display_name,
            c.username,
            c.specialties,
            c.bio,
            c.status.value if c.status else "",
            c.created_at.isoformat() if c.created_at else "",
        ])

    _log_export(current_user, "counselors", db)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=counselors_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/export/chat-sessions")
def export_chat_sessions(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.created_at.desc())
        .limit(5000)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["会话ID", "来访者ID", "咨询师ID", "状态", "风险等级", "风险摘要", "AI摘要", "创建时间"])
    for s in sessions:
        writer.writerow([
            s.id,
            s.visitor_id,
            s.counselor_id,
            s.status.value if s.status else "",
            s.risk_level.value if s.risk_level else "",
            s.risk_summary,
            s.ai_summary,
            s.created_at.isoformat() if s.created_at else "",
        ])

    _log_export(current_user, "chat-sessions", db)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=chat_sessions_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


def _log_export(admin: User, export_type: str, db: Session):
    log = ExportLog(
        admin_id=admin.id,
        admin_name=admin.display_name,
        export_type=export_type,
    )
    db.add(log)
    db.commit()


@router.get("/export-logs")
def list_export_logs(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(ExportLog)
        .order_by(ExportLog.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": l.id,
            "admin_id": l.admin_id,
            "admin_name": l.admin_name,
            "export_type": l.export_type,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


# ==================== 仪表盘统计 ====================

@router.get("/dashboard")
def dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_visitors = db.query(User).filter(User.role == UserRole.VISITOR, User.status == AccountStatus.ACTIVE).count()
    total_counselors = db.query(User).filter(User.role == UserRole.COUNSELOR, User.status == AccountStatus.ACTIVE).count()
    total_sessions = db.query(ChatSession).count()
    active_sessions = db.query(ChatSession).filter(ChatSession.status == "active").count()

    return {
        "total_visitors": total_visitors,
        "total_counselors": total_counselors,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
    }