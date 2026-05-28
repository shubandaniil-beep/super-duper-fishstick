from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.base import get_db
from app.db.models import Kindergarten
from app.schemas.kindergartens import KindergartenCreate, KindergartenUpdate, KindergartenOut
from app.api.dependencies import get_current_admin, get_current_superadmin

router = APIRouter(prefix="/kindergartens", tags=["kindergartens"])


@router.get("/", response_model=List[KindergartenOut])
async def list_kindergartens(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    result = await db.execute(select(Kindergarten).where(Kindergarten.is_active == True))
    return result.scalars().all()


@router.post("/", response_model=KindergartenOut)
async def create_kindergarten(
    data: KindergartenCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    kg = Kindergarten(**data.model_dump())
    db.add(kg)
    await db.commit()
    await db.refresh(kg)
    return kg


@router.get("/{kg_id}", response_model=KindergartenOut)
async def get_kindergarten(
    kg_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    result = await db.execute(select(Kindergarten).where(Kindergarten.id == kg_id))
    kg = result.scalar_one_or_none()
    if not kg:
        raise HTTPException(status_code=404, detail="Садик не найден")
    return kg


@router.put("/{kg_id}", response_model=KindergartenOut)
async def update_kindergarten(
    kg_id: str,
    data: KindergartenUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    result = await db.execute(select(Kindergarten).where(Kindergarten.id == kg_id))
    kg = result.scalar_one_or_none()
    if not kg:
        raise HTTPException(status_code=404, detail="Садик не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(kg, field, value)
    await db.commit()
    await db.refresh(kg)
    return kg
