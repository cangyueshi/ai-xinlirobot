import secrets
from sqlalchemy.orm import Session
from models.user import User, UserRole, AccountStatus
from utils.security import hash_password
from config import settings


def seed_super_admin(db: Session):
    existing = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
    if existing:
        return

    # 首次部署时生成随机密码，避免使用默认密码
    password = settings.SUPER_ADMIN_PASSWORD
    if password == "admin123456":
        password = secrets.token_urlsafe(12)
        print(f"⚠️  超级管理员已使用随机密码创建")
        print(f"   用户名: {settings.SUPER_ADMIN_USERNAME}")
        print(f"   密  码: {password}")
        print(f"   ⚠️ 首次登录后请立即修改密码！")

    admin = User(
        username=settings.SUPER_ADMIN_USERNAME,
        password_hash=hash_password(password),
        display_name="超级管理员",
        email=settings.SUPER_ADMIN_EMAIL or None,
        role=UserRole.SUPER_ADMIN,
        must_change_password=True,
    )
    db.add(admin)
    db.commit()