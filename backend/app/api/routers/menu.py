from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from app.db.base import get_db
from app.schemas.menu import MenuCreate, MenuOut
from app.services import menu_service
from app.api.dependencies import get_current_admin, get_current_teacher

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/", response_model=List[MenuOut])
async def get_menu(
    kg_id: str,
    target_date: date,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await menu_service.get_by_date(db, kg_id, target_date)


@router.post("/", response_model=MenuOut)
async def create_menu_item(
    data: MenuCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await menu_service.create(db, data)


@router.delete("/{menu_id}")
async def delete_menu_item(
    menu_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await menu_service.delete(db, menu_id):
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"ok": True}
