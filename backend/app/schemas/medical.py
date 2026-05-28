from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class MedicalRecordCreate(BaseModel):
    child_id: UUID
    record_type: str  # vaccination | illness | checkup
    title: str
    description: Optional[str] = None
    date: Optional[date] = None
    next_date: Optional[date] = None


class MedicalRecordOut(BaseModel):
    id: UUID
    child_id: UUID
    record_type: str
    title: str
    description: Optional[str]
    date: Optional[date]
    next_date: Optional[date]
    created_at: datetime

    model_config = {"from_attributes": True}
