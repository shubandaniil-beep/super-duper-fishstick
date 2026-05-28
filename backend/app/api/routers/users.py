from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.base import get_db
from app.schemas.users import UserCreate, UserUpdate, UserOut
from app.services import users_service
from app.api.dependencies import get_current_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
async def list_users(
    kg_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await users_service.get_all(db, kg_id, role)


@router.post("/", response_model=UserOut)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    return await users_service.create(db, data)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    user = await users_service.update(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await users_service.delete(db, user_id):
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"ok": True}
