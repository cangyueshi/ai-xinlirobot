import uuid
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole, AccountStatus, PasswordResetToken
from schemas.user import (
    UserLogin, WechatLogin, AdminLogin, UserResponse, TokenResponse,
    ChangePassword, ForceChangePassword, ForgotPassword, ResetPassword,
)
from utils.security import (
    hash_password, verify_password, create_mini_program_token, create_admin_token,
)
from utils.deps import get_current_user
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _build_user_response(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "openid": user.openid,
        "display_name": user.display_name,
        "role": user.role.value if isinstance(user.role, UserRole) else user.role,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "specialties": user.specialties,
        "status": user.status.value if isinstance(user.status, AccountStatus) else user.status,
        "must_change_password": user.must_change_password,
        "sub_admin_permissions": user.sub_admin_permissions,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _check_status(user: User):
    if user.status == AccountStatus.DISABLED:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    if user.status == AccountStatus.DELETED:
        raise HTTPException(status_code=403, detail="账号已被删除")


# ==================== 小程序端：微信登录（仅限 visitor） ====================

@router.post("/wechat-login")
def wechat_login(data: WechatLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == data.openid).first()

    if user and user.role != UserRole.VISITOR:
        raise HTTPException(status_code=403, detail="咨询师和管理员不能从小程序端登录，请使用管理后台")

    if not user:
        user = User(
            openid=data.openid,
            username=f"wx_{uuid.uuid4().hex[:12]}",
            display_name=data.display_name,
            avatar_url=data.avatar_url,
            role=UserRole.VISITOR,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    _check_status(user)
    token = create_mini_program_token({"sub": str(user.id), "role": user.role.value})
    user_dict = _build_user_response(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user_dict))


# ==================== 管理后台端：账号密码登录（咨询师/管理员） ====================

@router.post("/admin-login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.role == UserRole.VISITOR:
        raise HTTPException(status_code=403, detail="普通用户不能登录管理后台，请使用小程序")

    _check_status(user)
    token = create_admin_token({"sub": str(user.id), "role": user.role.value})

    user_dict = _build_user_response(user)
    resp = TokenResponse(access_token=token, user=UserResponse.model_validate(user_dict))

    if user.must_change_password:
        resp.access_token = token
        return {**resp.model_dump(), "must_change_password": True}

    return resp


# ==================== 保持兼容的旧登录接口 ====================

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    _check_status(user)
    token = create_admin_token({"sub": str(user.id), "role": user.role.value})
    user_dict = _build_user_response(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user_dict))


# ==================== 修改密码 ====================

@router.post("/change-password")
def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.old_password and current_user.password_hash:
        if not verify_password(data.old_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="原密码错误")

    current_user.password_hash = hash_password(data.new_password)
    current_user.must_change_password = False
    db.commit()
    return {"ok": True, "message": "密码修改成功"}


# ==================== 忘记密码 ====================

@router.post("/forgot-password")
def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"ok": True, "message": "如果该邮箱已注册，重置链接已发送"}

    if user.role == UserRole.VISITOR:
        raise HTTPException(status_code=400, detail="普通用户使用微信登录，无密码功能")

    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    recent = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.created_at > one_minute_ago,
        )
        .first()
    )
    if recent:
        raise HTTPException(status_code=429, detail="请60秒后再试")

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.created_at >= today_start,
        )
        .count()
    )
    if today_count >= 5:
        raise HTTPException(status_code=429, detail="今日重置次数已达上限（5次），请明天再试")

    token_str = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(reset_token)
    db.commit()

    _send_reset_email(user.email, token_str)
    return {"ok": True, "message": "如果该邮箱已注册，重置链接已发送"}


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == data.token, PasswordResetToken.used == False)
        .first()
    )
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="重置链接无效或已过期")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    reset_token.used = True
    db.commit()

    return {"ok": True, "message": "密码重置成功，请使用新密码登录"}


# ==================== 模拟邮件发送 ====================

def _send_reset_email(email: str, token: str):
    reset_url = f"http://localhost:8000/api/auth/reset-password?token={token}"
    print(f"[模拟邮件] 发送到 {email}，重置链接: {reset_url}")


# ==================== 当前用户信息 ====================

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _build_user_response(current_user)