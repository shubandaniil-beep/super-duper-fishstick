from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Group
from app.schemas.groups import GroupCreate, GroupUpdate


async def get(db: AsyncSession, group_id: str) -> Optional[Group]:
    result = await db.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, kg_id: str) -> List[Group]:
    result = await db.execute(select(Group).where(Group.kindergarten_id == kg_id))
    return result.scalars().all()


async def get_by_teacher(db: AsyncSession, teacher_id: str) -> Optional[Group]:
    result = await db.execute(select(Group).where(Group.teacher_id == teacher_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: GroupCreate) -> Group:
    group = Group(
        kindergarten_id=str(data.kindergarten_id),
        name=data.name,
        age_from=data.age_from,
        age_to=data.age_to,
        teacher_id=str(data.teacher_id) if data.teacher_id else None,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


async def update(db: AsyncSession, group_id: str, data: GroupUpdate) -> Optional[Group]:
    group = await get(db, group_id)
    if not group:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, str(value) if field.endswith("_id") and value else value)
    await db.commit()
    await db.refresh(group)
    return group


async def delete(db: AsyncSession, group_id: str) -> bool:
    group = await get(db, group_id)
    if not group:
        return False
    await db.delete(group)
    await db.commit()
    return True


async def count(db: AsyncSession, kg_id: str) -> int:
    result = await db.execute(select(func.count()).where(Group.kindergarten_id == kg_id))
    return result.scalar()
