from pydantic import BaseModel
from uuid import UUID
from datetime import time
from typing import Optional


class ScheduleCreate(BaseModel):
    group_id: UUID
    day_of_week: int  # 1=Mon ... 5=Fri
    time_start: time
    time_end: time
    subject: str
    teacher_id: Optional[UUID] = None
    room: Optional[str] = None


class ScheduleOut(BaseModel):
    id: UUID
    group_id: UUID
    day_of_week: int
    time_start: time
    time_end: time
    subject: str
    teacher_id: Optional[UUID]
    room: Optional[str]

    model_config = {"from_attributes": True}
