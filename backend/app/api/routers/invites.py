from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services import invite_service
from app.api.dependencies import get_current_admin
from app.db.models import User
from pydantic import BaseModel


class InviteRequest(BaseModel):
    kg_id: str
    role: str


router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("/generate")
async def generate_invite(
    data: InviteRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    code = await invite_service.generate(db, kg_id=data.kg_id, role=data.role)
    return {"code": code, "expires_in_days": 7}
