from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.base import get_db
from app.schemas.children import ChildCreate, ChildUpdate, ChildOut, ParentChildCreate
from app.services import children_service
from app.api.dependencies import get_current_admin, get_current_teacher

router = APIRouter(prefix="/children", tags=["children"])


@router.get("/", response_model=List[ChildOut])
async def list_children(
    kg_id: str,
    group_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await children_service.get_all(db, kg_id, group_id)


@router.post("/", response_model=ChildOut)
async def create_child(
    data: ChildCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await children_service.create(db, data)


@router.get("/{child_id}", response_model=ChildOut)
async def get_child(
    child_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    child = await children_service.get(db, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Ребёнок не найден")
    return child


@router.put("/{child_id}", response_model=ChildOut)
async def update_child(
    child_id: str,
    data: ChildUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    child = await children_service.update(db, child_id, data)
    if not child:
        raise HTTPException(status_code=404, detail="Ребёнок не найден")
    return child


@router.delete("/{child_id}")
async def archive_child(
    child_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await children_service.archive(db, child_id):
        raise HTTPException(status_code=404, detail="Ребёнок не найден")
    return {"ok": True}


@router.post("/link-parent")
async def link_parent(
    data: ParentChildCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    await children_service.link_parent(db, data)
    return {"ok": True}
