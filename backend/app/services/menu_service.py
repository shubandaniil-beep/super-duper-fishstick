from typing import List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Menu
from app.schemas.menu import MenuCreate


async def get_by_date(db: AsyncSession, kg_id: str, target_date: date) -> List[Menu]:
    result = await db.execute(
        select(Menu).where(Menu.kg_id == kg_id, Menu.date == target_date)
        .order_by(Menu.meal_type)
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: MenuCreate) -> Menu:
    item = Menu(
        kg_id=str(data.kg_id),
        date=data.date,
        meal_type=data.meal_type,
        description=data.description,
        calories=data.calories,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete(db: AsyncSession, menu_id: str) -> bool:
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    item = result.scalar_one_or_none()
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
