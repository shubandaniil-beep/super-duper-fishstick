from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class KindergartenCreate(BaseModel):
    name: str
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class KindergartenUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class KindergartenOut(BaseModel):
    id: UUID
    name: str
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
