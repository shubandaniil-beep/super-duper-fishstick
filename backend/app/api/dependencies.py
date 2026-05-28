from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models import User
from app.services.auth_service import decode_token
from app.services import users_service


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    user = await users_service.get_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    return user


async def get_current_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Нет доступа")
    return user


async def get_current_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("teacher", "admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    return user
