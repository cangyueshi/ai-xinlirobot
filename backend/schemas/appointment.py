from datetime import date, time
from pydantic import BaseModel, Field
from models.appointment import AppointmentStatus


class AvailabilityCreate(BaseModel):
    date: date
    start_time: time
    end_time: time


class AvailabilityBatchCreate(BaseModel):
    date: date
    time_slots: list[dict] = Field(default_factory=list)


class AvailabilityResponse(BaseModel):
    id: int
    counselor_id: int
    date: date
    start_time: time
    end_time: time
    is_booked: bool

    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    availability_id: int


class AppointmentResponse(BaseModel):
    id: int
    availability_id: int
    counselor_id: int
    visitor_id: int
    date: date
    start_time: time
    end_time: time
    status: AppointmentStatus
    notes: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}