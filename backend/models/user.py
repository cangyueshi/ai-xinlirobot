import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, Text, ForeignKey, func
from database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SUB_ADMIN = "sub_admin"
    COUNSELOR = "counselor"
    VISITOR = "visitor"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(100), unique=True, nullable=True, index=True)
    username = Column(String(50), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VISITOR)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    specialties = Column(Text, nullable=True)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    must_change_password = Column(Boolean, default=False)
    sub_admin_permissions = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class ExportLog(Base):
    __tablename__ = "export_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_name = Column(String(100), nullable=False)
    export_type = Column(String(50), nullable=False)
    filters_json = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())