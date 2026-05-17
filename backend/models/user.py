import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, func
from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COUNSELOR = "counselor"
    VISITOR = "visitor"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VISITOR)
    display_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())