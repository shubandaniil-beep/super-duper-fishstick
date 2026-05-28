from typing import List
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Schedule
from app.schemas.schedule import ScheduleCreate


async def get_by_group(db: AsyncSession, group_id: str) -> List[Schedule]:
    result = await db.execute(
        select(Schedule).where(Schedule.group_id == group_id)
        .order_by(Schedule.day_of_week, Schedule.time_start)
    )
    return result.scalars().all()


async def get_week(db: AsyncSession, group_id: str, monday: date) -> List[Schedule]:
    return await get_by_group(db, group_id)


async def create(db: AsyncSession, data: ScheduleCreate) -> Schedule:
    item = Schedule(
        group_id=str(data.group_id),
        day_of_week=data.day_of_week,
        time_start=data.time_start,
        time_end=data.time_end,
        subject=data.subject,
        teacher_id=str(data.teacher_id) if data.teacher_id else None,
        room=data.room,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete(db: AsyncSession, schedule_id: str) -> bool:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    item = result.scalar_one_or_none()
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
