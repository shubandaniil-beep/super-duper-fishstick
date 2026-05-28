from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List


class AttendanceCreate(BaseModel):
    child_id: UUID
    date: date
    status: str  # present | absent_sick | absent_vacation | absent_other
    note: Optional[str] = None


class AttendanceBulkCreate(BaseModel):
    group_id: UUID
    date: date
    records: List[AttendanceCreate]


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None


class AttendanceOut(BaseModel):
    id: UUID
    child_id: UUID
    date: date
    status: str
    note: Optional[str]
    marked_by: Optional[UUID]
    marked_at: datetime

    model_config = {"from_attributes": True}
