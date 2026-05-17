from sqlalchemy.orm import Session
from models.user import User, UserRole, AccountStatus
from utils.security import hash_password
from config import settings


def seed_super_admin(db: Session):
    existing = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
    if existing:
        return

    admin = User(
        username=settings.SUPER_ADMIN_USERNAME,
        password_hash=hash_password(settings.SUPER_ADMIN_PASSWORD),
        display_name="超级管理员",
        email=settings.SUPER_ADMIN_EMAIL or None,
        role=UserRole.SUPER_ADMIN,
        must_change_password=True,
    )
    db.add(admin)
    db.commit()