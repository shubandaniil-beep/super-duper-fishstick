from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class PostCreate(BaseModel):
    kg_id: UUID
    group_id: Optional[UUID] = None
    type: str  # news | announcement | photo
    title: Optional[str] = None
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None


class PostOut(BaseModel):
    id: UUID
    kg_id: UUID
    group_id: Optional[UUID]
    author_id: Optional[UUID]
    type: str
    title: Optional[str]
    content: Optional[str]
    media_urls: Optional[List[str]]
    created_at: datetime
    is_sent: bool

    model_config = {"from_attributes": True}
