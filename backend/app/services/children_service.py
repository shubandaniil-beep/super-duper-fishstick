from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Child, ParentChild
from app.schemas.children import ChildCreate, ChildUpdate, ParentChildCreate


async def get(db: AsyncSession, child_id: str) -> Optional[Child]:
    result = await db.execute(select(Child).where(Child.id == child_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, kg_id: str, group_id: Optional[str] = None) -> List[Child]:
    q = select(Child).where(Child.kindergarten_id == kg_id, Child.is_active == True)
    if group_id:
        q = q.where(Child.group_id == group_id)
    result = await db.execute(q)
    return result.scalars().all()


async def get_by_group(db: AsyncSession, group_id: str) -> List[Child]:
    result = await db.execute(
        select(Child).where(Child.group_id == group_id, Child.is_active == True)
        .order_by(Child.last_name, Child.first_name)
    )
    return result.scalars().all()


async def get_by_parent(db: AsyncSession, parent_id: str) -> List[Child]:
    result = await db.execute(
        select(Child).join(ParentChild, ParentChild.child_id == Child.id)
        .where(ParentChild.parent_id == parent_id, Child.is_active == True)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: ChildCreate) -> Child:
    child = Child(
        kindergarten_id=str(data.kindergarten_id),
        group_id=str(data.group_id),
        first_name=data.first_name,
        last_name=data.last_name,
        birth_date=data.birth_date,
        gender=data.gender,
        photo_url=data.photo_url,
        allergies=data.allergies,
        medical_notes=data.medical_notes,
    )
    db.add(child)
    await db.commit()
    await db.refresh(child)
    return child


async def update(db: AsyncSession, child_id: str, data: ChildUpdate) -> Optional[Child]:
    child = await get(db, child_id)
    if not child:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(child, field, str(value) if field.endswith("_id") and value else value)
    await db.commit()
    await db.refresh(child)
    return child


async def archive(db: AsyncSession, child_id: str) -> bool:
    child = await get(db, child_id)
    if not child:
        return False
    child.is_active = False
    await db.commit()
    return True


async def link_parent(db: AsyncSession, data: ParentChildCreate) -> ParentChild:
    link = ParentChild(
        parent_id=str(data.parent_id),
        child_id=str(data.child_id),
        relation=data.relation,
    )
    db.add(link)
    await db.commit()
    return link


async def count(db: AsyncSession, kg_id: str) -> int:
    result = await db.execute(
        select(func.count()).where(Child.kindergarten_id == kg_id, Child.is_active == True)
    )
    return result.scalar()
