from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.base import get_db
from app.schemas.posts import PostCreate, PostOut
from app.services import posts_service
from app.api.dependencies import get_current_admin, get_current_teacher
from app.db.models import User

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostOut])
async def list_posts(
    kg_id: str,
    group_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await posts_service.get_all(db, kg_id, group_id)


@router.post("/", response_model=PostOut)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    return await posts_service.create(db, data, author_id=str(current_user.id))


@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    if not await posts_service.delete(db, post_id):
        raise HTTPException(status_code=404, detail="Пост не найден")
    return {"ok": True}
