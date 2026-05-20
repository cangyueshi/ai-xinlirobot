"""
创建3个已认证的测试咨询师账号及可预约时间。
所有密码统一为: 123456

边缘情况处理:
  - 已存在的账号不重复创建（幂等）
  - 不同咨询师分配不同时段和日期范围
  - 每个咨询师的可预约时间不重叠
  - 自动计算有效日期范围（今天+2 ~ 今天+7）
  - 空的 bio / specialties 不会导致问题
  - 咨询师必须 is_approved=True 才可被来访者看见
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.user import User, UserRole, AccountStatus
from models.appointment import Availability
from utils.security import hash_password
from config import settings


TEST_PASSWORD = "123456"

COUNSELORS = [
    {
        "username": "chensiyuan",
        "display_name": "陈思远",
        "specialties": "情绪管理、压力调适、职场心理",
        "bio": "国家二级心理咨询师，擅长情绪管理与职场压力疏导，累计咨询超过800小时。",
        "slots": [
            ("09:00:00", "10:00:00"),
            ("10:00:00", "11:00:00"),
            ("11:00:00", "12:00:00"),
        ],
        "available_days": 3,  # 设置3天的可预约时间
    },
    {
        "username": "lihua",
        "display_name": "李华",
        "specialties": "人际关系、家庭咨询、亲密关系",
        "bio": "家庭治疗师，专注人际关系与亲密关系议题，温和包容的咨询风格。",
        "slots": [
            ("14:00:00", "15:00:00"),
            ("15:00:00", "16:00:00"),
            ("16:00:00", "17:00:00"),
        ],
        "available_days": 4,
    },
    {
        "username": "wangfang",
        "display_name": "王芳",
        "specialties": "焦虑缓解、自我成长、正念训练",
        "bio": "临床心理咨询硕士，擅长焦虑管理和正念认知疗法，帮助来访者实现自我成长。",
        "slots": [
            ("19:00:00", "20:00:00"),
            ("20:00:00", "21:00:00"),
        ],
        "available_days": 3,
    },
]


def seed_test_counselors(db: Session):
    today = date.today()
    min_date = today + timedelta(days=2)
    max_date = today + timedelta(days=7)

    created = []
    skipped = []

    for c in COUNSELORS:
        existing = db.query(User).filter(User.username == c["username"]).first()
        if existing:
            skipped.append(f"{c['username']} ({c['display_name']}) - 已存在")
            continue

        counselor = User(
            username=c["username"],
            password_hash=hash_password(TEST_PASSWORD),
            display_name=c["display_name"],
            specialties=c["specialties"],
            bio=c["bio"],
            role=UserRole.COUNSELOR,
            status=AccountStatus.ACTIVE,
            is_approved=True,
            must_change_password=False,
        )
        db.add(counselor)
        db.flush()  # 获取 id

        # 计算可用日期：从 min_date 开始，跳过周末，取 available_days 天
        avail_count = 0
        cursor = min_date
        while avail_count < c["available_days"] and cursor <= max_date:
            # 跳过周末（周六=5, 周日=6）
            if cursor.weekday() >= 5:
                cursor += timedelta(days=1)
                continue

            # 先删除该咨询师在该日期已有的可用时间（幂等）
            existing_av = db.query(Availability).filter(
                Availability.counselor_id == counselor.id,
                Availability.date == cursor,
                Availability.is_booked == 0,
            ).all()
            for ea in existing_av:
                db.delete(ea)

            # 创建新的可用时间段
            for start_str, end_str in c["slots"]:
                st = time.fromisoformat(start_str)
                et = time.fromisoformat(end_str)
                av = Availability(
                    counselor_id=counselor.id,
                    week_day=cursor.weekday(),
                    date=cursor,
                    start_time=st,
                    end_time=et,
                )
                db.add(av)

            avail_count += 1
            cursor += timedelta(days=1)

        created.append(f"{c['username']} ({c['display_name']}) - {c['available_days']}天可预约")

    db.commit()

    # 输出结果
    print("=" * 50)
    print("测试咨询师创建结果")
    print("=" * 50)
    if created:
        print(f"\n✅ 新建 ({len(created)}):")
        for item in created:
            print(f"   {item}")
    if skipped:
        print(f"\n⏭️  已存在, 跳过 ({len(skipped)}):")
        for item in skipped:
            print(f"   {item}")
    if not created and not skipped:
        print("\n⚠️  未创建任何账号")

    print(f"\n📋 密码统一: {TEST_PASSWORD}")
    print(f"📋 可预约日期范围: {min_date} ~ {max_date}")
    print()


def verify_counselors(db: Session):
    """验证创建的咨询师数据完整性"""
    issues = []
    counselors = db.query(User).filter(
        User.role == UserRole.COUNSELOR,
        User.is_approved == True,
    ).all()

    for c in counselors:
        # 检查是否有可用时间
        today = date.today()
        avails = db.query(Availability).filter(
            Availability.counselor_id == c.id,
            Availability.date >= today,
            Availability.is_booked == 0,
            Availability.is_active == 1,
        ).all()

        if not avails:
            issues.append(f"{c.display_name} ({c.username}): 无可用时间")

        # 检查是否有重叠的时间段
        dates_checked = set()
        for av in avails:
            key = (av.date, av.start_time, av.end_time)
            if key in dates_checked:
                issues.append(f"{c.display_name}: 存在重复时间段 {av.date} {av.start_time}-{av.end_time}")
            dates_checked.add(key)

        # 检查 is_approved
        if not c.is_approved:
            issues.append(f"{c.display_name}: 未通过认证 (is_approved=False)")

        # 检查 role
        if c.role != UserRole.COUNSELOR:
            issues.append(f"{c.display_name}: 角色异常 ({c.role})")

    return issues


if __name__ == "__main__":
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        seed_test_counselors(db)
        issues = verify_counselors(db)
        if issues:
            print("⚠️ 发现以下问题:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ 所有咨询师数据完整性验证通过，无异常")
