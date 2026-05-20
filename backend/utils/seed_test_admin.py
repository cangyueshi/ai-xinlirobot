"""
创建测试管理账号。
当正式超级管理员（id=1, username=admin）首次登录后，该测试账号将自动作废。
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import secrets
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.user import User, UserRole, AccountStatus
from utils.security import hash_password
from config import settings

TEST_USERNAME = "test_admin"
TEST_PASSWORD = secrets.token_urlsafe(8)


def seed_test_admin(db: Session):
    existing = db.query(User).filter(User.username == TEST_USERNAME).first()
    if existing:
        print(f"测试账号 {TEST_USERNAME} 已存在")
        return

    admin = User(
        username=TEST_USERNAME,
        password_hash=hash_password(TEST_PASSWORD),
        display_name="测试管理员（待作废）",
        role=UserRole.SUB_ADMIN,
        must_change_password=False,
    )
    db.add(admin)
    db.commit()
    print(f"✅ 测试管理账号已创建")
    print(f"   用户名: {TEST_USERNAME}")
    print(f"   密  码: {TEST_PASSWORD}")
    print(f"   ⚠️ 正式超级管理员登录后，此账号将自动禁用")


if __name__ == "__main__":
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        seed_test_admin(db)
