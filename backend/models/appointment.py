import enum
from sqlalchemy import Column, Integer, String, Date, Time, Enum, ForeignKey, DateTime, func
from database import Base


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Availability(Base):
    __tablename__ = "availabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_booked = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    availability_id = Column(Integer, ForeignKey("availabilities.id"), nullable=False)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.BOOKED)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())