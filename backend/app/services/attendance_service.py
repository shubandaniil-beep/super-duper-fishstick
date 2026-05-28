from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.models import Attendance, Child
from app.schemas.attendance import AttendanceCreate, AttendanceBulkCreate, AttendanceUpdate


async def get(db: AsyncSession, attendance_id: str) -> Optional[Attendance]:
    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    return result.scalar_one_or_none()


async def get_today(db: AsyncSession, child_id: str) -> Optional[Attendance]:
    result = await db.execute(
        select(Attendance).where(Attendance.child_id == child_id, Attendance.date == date.today())
    )
    return result.scalar_one_or_none()


async def get_by_date(db: AsyncSession, kg_id: str, target_date: date, group_id: Optional[str] = None) -> List[Attendance]:
    q = (
        select(Attendance).join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date == target_date)
    )
    if group_id:
        q = q.where(Child.group_id == group_id)
    result = await db.execute(q)
    return result.scalars().all()


async def get_month(db: AsyncSession, child_id: str, year: int, month: int) -> List[Attendance]:
    from calendar import monthrange
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    result = await db.execute(
        select(Attendance).where(
            Attendance.child_id == child_id,
            Attendance.date >= first_day,
            Attendance.date <= last_day,
        ).order_by(Attendance.date)
    )
    return result.scalars().all()


async def bulk_mark(db: AsyncSession, data: AttendanceBulkCreate, marked_by: str) -> List[Attendance]:
    results = []
    for record in data.records:
        existing = await db.execute(
            select(Attendance).where(
                Attendance.child_id == str(record.child_id),
                Attendance.date == record.date,
            )
        )
        att = existing.scalar_one_or_none()
        if att:
            att.status = record.status
            att.note = record.note
            att.marked_by = marked_by
        else:
            att = Attendance(
                child_id=str(record.child_id),
                date=record.date,
                status=record.status,
                note=record.note,
                marked_by=marked_by,
            )
            db.add(att)
        results.append(att)
    await db.commit()
    return results


async def update_one(db: AsyncSession, attendance_id: str, data: AttendanceUpdate) -> Optional[Attendance]:
    att = await get(db, attendance_id)
    if not att:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(att, field, value)
    await db.commit()
    await db.refresh(att)
    return att


async def count_present(db: AsyncSession, kg_id: str, target_date: date) -> int:
    result = await db.execute(
        select(func.count()).select_from(Attendance)
        .join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date == target_date, Attendance.status == "present")
    )
    return result.scalar()


async def count_absent(db: AsyncSession, kg_id: str, target_date: date) -> int:
    result = await db.execute(
        select(func.count()).select_from(Attendance)
        .join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date == target_date, Attendance.status != "present")
    )
    return result.scalar()


async def percent_this_month(db: AsyncSession, kg_id: str) -> float:
    today = date.today()
    first_day = date(today.year, today.month, 1)
    total = await db.execute(
        select(func.count()).select_from(Attendance)
        .join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date >= first_day, Attendance.date <= today)
    )
    present = await db.execute(
        select(func.count()).select_from(Attendance)
        .join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date >= first_day,
               Attendance.date <= today, Attendance.status == "present")
    )
    total_val = total.scalar() or 0
    present_val = present.scalar() or 0
    return round(present_val / total_val * 100, 1) if total_val else 0.0


async def is_marked_today(db: AsyncSession, group_id: str) -> bool:
    result = await db.execute(
        select(func.count()).select_from(Attendance)
        .join(Child, Child.id == Attendance.child_id)
        .where(Child.group_id == group_id, Attendance.date == date.today())
    )
    return (result.scalar() or 0) > 0


async def get_report(db: AsyncSession, kg_id: str, date_from: date, date_to: date,
                     group_id: Optional[str] = None) -> List[Attendance]:
    q = (
        select(Attendance).join(Child, Child.id == Attendance.child_id)
        .where(Child.kindergarten_id == kg_id, Attendance.date >= date_from, Attendance.date <= date_to)
    )
    if group_id:
        q = q.where(Child.group_id == group_id)
    result = await db.execute(q.order_by(Attendance.date, Child.last_name))
    return result.scalars().all()
