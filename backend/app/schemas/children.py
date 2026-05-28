from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class ChildCreate(BaseModel):
    kindergarten_id: UUID
    group_id: UUID
    first_name: str
    last_name: str
    birth_date: date
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None


class ChildUpdate(BaseModel):
    group_id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    is_active: Optional[bool] = None


class ChildOut(BaseModel):
    id: UUID
    kindergarten_id: UUID
    group_id: UUID
    first_name: str
    last_name: str
    birth_date: date
    gender: Optional[str]
    photo_url: Optional[str]
    allergies: Optional[str]
    medical_notes: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ParentChildCreate(BaseModel):
    parent_id: UUID
    child_id: UUID
    relation: Optional[str] = None
