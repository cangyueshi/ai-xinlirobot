from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from models.appointment import Availability, Appointment, AppointmentStatus
from schemas.appointment import AvailabilityBatchCreate, AppointmentCreate
from schemas.user import UserResponse
from utils.deps import get_current_user, require_role

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def _serialize_av(av: Availability):
    return {
        "id": av.id,
        "counselor_id": av.counselor_id,
        "date": av.date.isoformat() if av.date else None,
        "start_time": av.start_time.isoformat() if av.start_time else None,
        "end_time": av.end_time.isoformat() if av.end_time else None,
        "is_booked": bool(av.is_booked),
    }


def _serialize_apt(apt: Appointment):
    return {
        "id": apt.id,
        "availability_id": apt.availability_id,
        "backup_availability_id": apt.backup_availability_id,
        "counselor_id": apt.counselor_id,
        "visitor_id": apt.visitor_id,
        "visitor_name": apt.visitor.display_name if apt.visitor else None,
        "counselor_name": apt.counselor.display_name if apt.counselor else None,
        "date": apt.date.isoformat() if apt.date else None,
        "start_time": apt.start_time.isoformat() if apt.start_time else None,
        "end_time": apt.end_time.isoformat() if apt.end_time else None,
        "status": apt.status.value if apt.status else "pending",
        "notes": apt.notes,
        "confirmed_at": apt.confirmed_at.isoformat() if apt.confirmed_at else None,
        "created_at": apt.created_at.isoformat() if apt.created_at else None,
    }


# ==================== 咨询师：批量设置可用时间 ====================

DAILY_SLOTS = [
    ("09:00:00", "10:00:00"),
    ("10:00:00", "11:00:00"),
    ("11:00:00", "12:00:00"),
    ("12:30:00", "13:30:00"),
    ("13:30:00", "14:30:00"),
    ("14:30:00", "15:30:00"),
    ("15:30:00", "16:30:00"),
    ("19:00:00", "20:00:00"),
]


@router.post("/availabilities/batch")
def set_availabilities(
    data: AvailabilityBatchCreate,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    wd = data.date.weekday()

    db.query(Availability).filter(
        Availability.counselor_id == current_user.id,
        Availability.date == data.date,
        Availability.is_booked == 0,
    ).delete()

    created = 0
    for slot in data.time_slots:
        st_str = slot["start_time"]
        et_str = slot["end_time"]
        st = time.fromisoformat(st_str) if isinstance(st_str, str) else st_str
        et = time.fromisoformat(et_str) if isinstance(et_str, str) else et_str
        av = Availability(
            counselor_id=current_user.id,
            week_day=wd,
            date=data.date,
            start_time=st,
            end_time=et,
        )
        db.add(av)
        created += 1
    db.commit()
    return {"date": data.date.isoformat(), "count": created}


@router.get("/availabilities/mine")
def get_my_availabilities(
    d: date | None = None,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    q = db.query(Availability).filter(Availability.counselor_id == current_user.id)
    if d:
        q = q.filter(Availability.date == d)
    result = q.order_by(Availability.date, Availability.start_time).all()
    return [_serialize_av(av) for av in result]


# ==================== 来访者：查看咨询师 & 预约 ====================

@router.get("/counselors")
def list_counselors(db: Session = Depends(get_db)):
    counselors = db.query(User).filter(
        User.role == UserRole.COUNSELOR,
        User.is_active == True,
    ).all()
    return [{"id": c.id, "display_name": c.display_name, "phone": c.phone} for c in counselors]


@router.get("/availabilities/{counselor_id}")
def get_counselor_availabilities(
    counselor_id: int,
    d: date | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Availability).filter(
        Availability.counselor_id == counselor_id,
        Availability.is_booked == 0,
        Availability.is_active == 1,
    )
    if d:
        q = q.filter(Availability.date == d)
    result = q.order_by(Availability.date, Availability.start_time).all()
    return [_serialize_av(av) for av in result]


@router.post("/book")
def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    av = db.query(Availability).filter(Availability.id == data.availability_id, Availability.is_booked == 0).first()
    if not av:
        raise HTTPException(status_code=400, detail="该时间段不可用")

    av.is_booked = 1

    if data.backup_availability_id:
        backup_av = db.query(Availability).filter(
            Availability.id == data.backup_availability_id, Availability.is_booked == 0
        ).first()
        if backup_av:
            backup_av.is_booked = 1

    apt = Appointment(
        availability_id=av.id,
        backup_availability_id=data.backup_availability_id,
        counselor_id=av.counselor_id,
        visitor_id=current_user.id,
        date=av.date,
        start_time=av.start_time,
        end_time=av.end_time,
        status=AppointmentStatus.PENDING,
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return _serialize_apt(apt)


# ==================== 通用：查看/取消预约 ====================

@router.get("/mine")
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == UserRole.COUNSELOR:
        q = db.query(Appointment).filter(Appointment.counselor_id == current_user.id)
    else:
        q = db.query(Appointment).filter(Appointment.visitor_id == current_user.id)
    result = q.order_by(Appointment.date.desc(), Appointment.start_time).all()
    return [_serialize_apt(apt) for apt in result]


@router.post("/{apt_id}/cancel")
def cancel_appointment(
    apt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在")
    is_owner = (
        (current_user.role == UserRole.VISITOR and apt.visitor_id == current_user.id)
        or (current_user.role == UserRole.COUNSELOR and apt.counselor_id == current_user.id)
    )
    if not is_owner:
        raise HTTPException(status_code=403, detail="无权操作")

    apt.status = AppointmentStatus.CANCELLED
    for aid in [apt.availability_id, apt.backup_availability_id]:
        if aid:
            av = db.query(Availability).filter(Availability.id == aid).first()
            if av:
                av.is_booked = 0
    db.commit()
    return {"ok": True}


# ==================== 咨询师：确认预约 ====================

@router.post("/{apt_id}/confirm")
def confirm_appointment(
    apt_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    apt = db.query(Appointment).filter(
        Appointment.id == apt_id,
        Appointment.counselor_id == current_user.id,
        Appointment.status == AppointmentStatus.PENDING,
    ).first()
    if not apt:
        raise HTTPException(status_code=404, detail="预约不存在或已处理")

    apt.status = AppointmentStatus.CONFIRMED
    apt.confirmed_at = datetime.now(timezone.utc)

    if apt.backup_availability_id:
        backup_av = db.query(Availability).filter(
            Availability.id == apt.backup_availability_id
        ).first()
        if backup_av:
            backup_av.is_booked = 0

    db.commit()
    return {"ok": True, "message": "预约已确认，来访者将收到通知", "visitor_id": apt.visitor_id}