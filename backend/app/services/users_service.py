from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import User, ParentChild
from app.schemas.users import UserCreate, UserUpdate
from app.services.auth_service import hash_password


async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, kg_id: str, role: Optional[str] = None) -> List[User]:
    q = select(User).where(User.kindergarten_id == kg_id, User.is_active == True)
    if role:
        q = q.where(User.role == role)
    result = await db.execute(q)
    return result.scalars().all()


async def get_all_teachers(db: AsyncSession) -> List[User]:
    result = await db.execute(select(User).where(User.role == "teacher", User.is_active == True))
    return result.scalars().all()


async def get_parents(db: AsyncSession, child_id: str) -> List[User]:
    result = await db.execute(
        select(User).join(ParentChild, ParentChild.parent_id == User.id)
        .where(ParentChild.child_id == child_id)
    )
    return result.scalars().all()


async def get_parents_for_target(db: AsyncSession, kg_id: str, group_id: Optional[str] = None) -> List[User]:
    from app.db.models import Child
    q = (
        select(User).join(ParentChild, ParentChild.parent_id == User.id)
        .join(Child, Child.id == ParentChild.child_id)
        .where(Child.kindergarten_id == kg_id, Child.is_active == True)
    )
    if group_id:
        q = q.where(Child.group_id == group_id)
    result = await db.execute(q)
    return result.scalars().all()


async def create(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        kindergarten_id=str(data.kindergarten_id) if data.kindergarten_id else None,
        role=data.role,
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password) if data.password else None,
        telegram_id=data.telegram_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update(db: AsyncSession, user_id: str, data: UserUpdate) -> Optional[User]:
    user = await get_by_id(db, user_id)
    if not user:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user_id: str) -> bool:
    user = await get_by_id(db, user_id)
    if not user:
        return False
    user.is_active = False
    await db.commit()
    return True


async def count_by_role(db: AsyncSession, kg_id: str, role: str) -> int:
    result = await db.execute(
        select(func.count()).where(User.kindergarten_id == kg_id, User.role == role, User.is_active == True)
    )
    return result.scalar()


async def link_telegram(db: AsyncSession, user_id: str, telegram_id: int, username: Optional[str] = None) -> bool:
    user = await get_by_id(db, user_id)
    if not user:
        return False
    user.telegram_id = telegram_id
    if username:
        user.telegram_username = username
    await db.commit()
    return True
