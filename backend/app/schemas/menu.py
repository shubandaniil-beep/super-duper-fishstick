from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional


class MenuCreate(BaseModel):
    kg_id: UUID
    date: date
    meal_type: str  # breakfast | lunch | snack | dinner
    description: str
    calories: Optional[int] = None


class MenuOut(BaseModel):
    id: UUID
    kg_id: UUID
    date: date
    meal_type: str
    description: str
    calories: Optional[int]

    model_config = {"from_attributes": True}
