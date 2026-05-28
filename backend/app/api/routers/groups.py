from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.schemas.groups import GroupCreate, GroupUpdate, GroupOut
from app.services import groups_service
from app.api.dependencies import get_current_admin

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupOut])
async def list_groups(
    kg_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await groups_service.get_all(db, kg_id)


@router.post("/", response_model=GroupOut)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await groups_service.create(db, data)


@router.put("/{group_id}", response_model=GroupOut)
async def update_group(
    group_id: str,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    group = await groups_service.update(db, group_id, data)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await groups_service.delete(db, group_id):
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return {"ok": True}
