"""内测数据初始化：创建测试咨询师账号（可通过环境变量覆盖配置）"""

import os
from database import SessionLocal
from models.user import User, UserRole
from utils.security import hash_password

TEST_COUNSELOR_USERNAME = os.getenv("TEST_COUNSELOR_USERNAME", "counselor_test")
TEST_COUNSELOR_PASSWORD = os.getenv("TEST_COUNSELOR_PASSWORD", "test123456")
TEST_COUNSELOR_NAME = os.getenv("TEST_COUNSELOR_NAME", "测试咨询师")


def seed_test_counselor():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == TEST_COUNSELOR_USERNAME).first()
        if existing:
            print(f"[测试数据] 咨询师账号已存在: {TEST_COUNSELOR_USERNAME}")
            return

        counselor = User(
            username=TEST_COUNSELOR_USERNAME,
            password_hash=hash_password(TEST_COUNSELOR_PASSWORD),
            display_name=TEST_COUNSELOR_NAME,
            role=UserRole.COUNSELOR,
            bio="内测用咨询师账号",
            specialties="考试焦虑、人际关系、情绪管理",
            must_change_password=False,
        )
        db.add(counselor)
        db.commit()
        print(f"[测试数据] 咨询师账号已创建: {TEST_COUNSELOR_USERNAME} / {TEST_COUNSELOR_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_counselor()
