from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    kindergarten_id: Optional[UUID] = None
    role: str
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    telegram_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    group_id: Optional[UUID] = None


class UserOut(BaseModel):
    id: UUID
    kindergarten_id: Optional[UUID]
    role: str
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    telegram_id: Optional[int]
    telegram_username: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
