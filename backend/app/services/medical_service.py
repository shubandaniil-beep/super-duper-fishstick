from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import MedicalRecord
from app.schemas.medical import MedicalRecordCreate


async def get_by_child(db: AsyncSession, child_id: str) -> List[MedicalRecord]:
    result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.child_id == child_id)
        .order_by(MedicalRecord.date.desc())
    )
    return result.scalars().all()


async def create(db: AsyncSession, data: MedicalRecordCreate) -> MedicalRecord:
    record = MedicalRecord(
        child_id=str(data.child_id),
        record_type=data.record_type,
        title=data.title,
        description=data.description,
        date=data.date,
        next_date=data.next_date,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
