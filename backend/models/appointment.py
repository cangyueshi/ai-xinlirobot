import enum
from sqlalchemy import Column, Integer, String, Date, Time, Enum, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from database import Base


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_day = Column(Integer, nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Integer, default=1)
    is_booked = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    availability_id = Column(Integer, ForeignKey("availabilities.id"), nullable=False)
    backup_availability_id = Column(Integer, ForeignKey("availabilities.id"), nullable=True)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(String(500), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    visitor = relationship("User", foreign_keys=[visitor_id], lazy="joined")
    counselor = relationship("User", foreign_keys=[counselor_id], lazy="joined")