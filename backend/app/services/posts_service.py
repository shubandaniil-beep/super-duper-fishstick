from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.db.models import Post
from app.schemas.posts import PostCreate


async def get_feed(db: AsyncSession, kg_id: str, group_id: Optional[str] = None, limit: int = 20) -> List[Post]:
    q = select(Post).where(
        Post.kg_id == kg_id,
        or_(Post.group_id == group_id, Post.group_id == None) if group_id else Post.kg_id == kg_id
    ).order_by(Post.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


async def get_all(db: AsyncSession, kg_id: str, group_id: Optional[str] = None) -> List[Post]:
    q = select(Post).where(Post.kg_id == kg_id)
    if group_id:
        q = q.where(Post.group_id == group_id)
    result = await db.execute(q.order_by(Post.created_at.desc()))
    return result.scalars().all()


async def create(db: AsyncSession, data: PostCreate, author_id: str) -> Post:
    post = Post(
        kg_id=str(data.kg_id),
        group_id=str(data.group_id) if data.group_id else None,
        author_id=author_id,
        type=data.type,
        title=data.title,
        content=data.content,
        media_urls=data.media_urls,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def mark_sent(db: AsyncSession, post_id: str) -> None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post:
        post.is_sent = True
        await db.commit()


async def delete(db: AsyncSession, post_id: str) -> bool:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        return False
    await db.delete(post)
    await db.commit()
    return True
