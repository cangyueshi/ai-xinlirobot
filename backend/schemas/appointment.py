from datetime import date, time
from pydantic import BaseModel, Field
from models.appointment import AppointmentStatus


class AvailabilityBatchCreate(BaseModel):
    date: date
    time_slots: list[dict] = Field(default_factory=list)


class AppointmentCreate(BaseModel):
    availability_id: int
    backup_availability_id: int | None = None


class AppointmentConfirm(BaseModel):
    confirmed: bool = True