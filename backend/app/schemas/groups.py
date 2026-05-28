from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GroupCreate(BaseModel):
    kindergarten_id: UUID
    name: str
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    teacher_id: Optional[UUID] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    age_from: Optional[int] = None
    age_to: Optional[int] = None
    teacher_id: Optional[UUID] = None


class GroupOut(BaseModel):
    id: UUID
    kindergarten_id: UUID
    name: str
    age_from: Optional[int]
    age_to: Optional[int]
    teacher_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
