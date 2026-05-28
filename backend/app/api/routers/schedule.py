from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleOut
from app.services import schedule_service
from app.api.dependencies import get_current_admin, get_current_teacher

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/", response_model=List[ScheduleOut])
async def get_schedule(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await schedule_service.get_by_group(db, group_id)


@router.post("/", response_model=ScheduleOut)
async def create_schedule_item(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await schedule_service.create(db, data)


@router.delete("/{schedule_id}")
async def delete_schedule_item(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await schedule_service.delete(db, schedule_id):
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"ok": True}
