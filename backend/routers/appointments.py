from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from models.appointment import Availability, Appointment, AppointmentStatus
from schemas.appointment import (
    AvailabilityCreate,
    AvailabilityBatchCreate,
    AvailabilityResponse,
    AppointmentCreate,
    AppointmentResponse,
)
from schemas.user import UserResponse
from utils.deps import get_current_user, require_role

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def serialize_appointment(apt: Appointment) -> dict:
    return {
        "id": apt.id,
        "availability_id": apt.availability_id,
        "counselor_id": apt.counselor_id,
        "visitor_id": apt.visitor_id,
        "date": apt.date.isoformat() if apt.date else None,
        "start_time": apt.start_time.isoformat() if apt.start_time else None,
        "end_time": apt.end_time.isoformat() if apt.end_time else None,
        "status": apt.status,
        "notes": apt.notes,
        "created_at": apt.created_at.isoformat() if apt.created_at else None,
    }


def serialize_availability(av: Availability) -> dict:
    return {
        "id": av.id,
        "counselor_id": av.counselor_id,
        "date": av.date.isoformat() if av.date else None,
        "start_time": av.start_time.isoformat() if av.start_time else None,
        "end_time": av.end_time.isoformat() if av.end_time else None,
        "is_booked": bool(av.is_booked),
    }


# ==================== 咨询师：管理可用时间 ====================

@router.post("/availabilities", response_model=AvailabilityResponse)
def add_availability(
    data: AvailabilityCreate,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    if data.start_time >= data.end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")

    av = Availability(
        counselor_id=current_user.id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(av)
    db.commit()
    db.refresh(av)
    return serialize_availability(av)


@router.post("/availabilities/batch")
def add_availabilities_batch(
    data: AvailabilityBatchCreate,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    created = []
    for slot in data.time_slots:
        av = Availability(
            counselor_id=current_user.id,
            date=data.date,
            start_time=slot["start_time"],
            end_time=slot["end_time"],
        )
        db.add(av)
        created.append(av)
    db.commit()
    return {"count": len(created)}


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
    return [serialize_availability(av) for av in result]


@router.delete("/availabilities/{av_id}")
def delete_availability(
    av_id: int,
    current_user: User = Depends(require_role("counselor")),
    db: Session = Depends(get_db),
):
    av = db.query(Availability).filter(
        Availability.id == av_id,
        Availability.counselor_id == current_user.id,
    ).first()
    if not av:
        raise HTTPException(status_code=404, detail="时间段不存在")
    if av.is_booked:
        raise HTTPException(status_code=400, detail="已被预约，无法删除")
    db.delete(av)
    db.commit()
    return {"ok": True}


# ==================== 来访者：查看咨询师 & 预约 ====================

@router.get("/counselors")
def list_counselors(db: Session = Depends(get_db)):
    counselors = db.query(User).filter(
        User.role == UserRole.COUNSELOR,
        User.is_active == True,
    ).all()
    return [
        {"id": c.id, "display_name": c.display_name, "phone": c.phone}
        for c in counselors
    ]


@router.get("/availabilities/{counselor_id}")
def get_counselor_availabilities(
    counselor_id: int,
    d: date | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Availability).filter(
        Availability.counselor_id == counselor_id,
        Availability.is_booked == 0,
    )
    if d:
        q = q.filter(Availability.date == d)
    result = q.order_by(Availability.date, Availability.start_time).all()
    return [serialize_availability(av) for av in result]


@router.post("/book")
def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_role("visitor")),
    db: Session = Depends(get_db),
):
    av = db.query(Availability).filter(Availability.id == data.availability_id).first()
    if not av:
        raise HTTPException(status_code=404, detail="该时间段不存在")
    if av.is_booked:
        raise HTTPException(status_code=400, detail="该时间段已被预约")

    existing = db.query(Appointment).filter(
        Appointment.visitor_id == current_user.id,
        Appointment.date == av.date,
        Appointment.start_time == av.start_time,
        Appointment.status != AppointmentStatus.CANCELLED,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您在该时段已有预约")

    av.is_booked = 1
    apt = Appointment(
        availability_id=av.id,
        counselor_id=av.counselor_id,
        visitor_id=current_user.id,
        date=av.date,
        start_time=av.start_time,
        end_time=av.end_time,
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return serialize_appointment(apt)


# ==================== 通用：查看预约 & 取消 ====================

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
    return [serialize_appointment(apt) for apt in result]


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
    av = db.query(Availability).filter(Availability.id == apt.availability_id).first()
    if av:
        av.is_booked = 0
    db.commit()
    return {"ok": True}