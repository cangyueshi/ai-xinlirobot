from __future__ import annotations

from datetime import date as date_type, time
from typing import Optional
from pydantic import BaseModel, Field
from models.appointment import AppointmentStatus


class AvailabilityBatchCreate(BaseModel):
    date: Optional[date_type] = None
    date_range: Optional[list[date_type]] = None  # [start_date, end_date]
    time_slots: list[dict] = Field(default_factory=list)


class AppointmentCreate(BaseModel):
    availability_id: int
    backup_availability_id: int | None = None
    reason: str | None = None


class AppointmentConfirm(BaseModel):
    confirmed: bool = True
