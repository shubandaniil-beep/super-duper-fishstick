from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from app.db.base import get_db
from app.schemas.attendance import AttendanceBulkCreate, AttendanceUpdate, AttendanceOut
from app.services import attendance_service
from app.api.dependencies import get_current_admin, get_current_teacher, get_current_user
from app.db.models import User

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/", response_model=List[AttendanceOut])
async def get_attendance(
    kg_id: str,
    target_date: date,
    group_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await attendance_service.get_by_date(db, kg_id, target_date, group_id)


@router.post("/bulk")
async def mark_bulk_attendance(
    data: AttendanceBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    result = await attendance_service.bulk_mark(db, data, marked_by=str(current_user.id))
    return {"marked": len(result), "date": str(data.date)}


@router.put("/{attendance_id}", response_model=AttendanceOut)
async def update_attendance(
    attendance_id: str,
    data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    att = await attendance_service.update_one(db, attendance_id, data)
    if not att:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return att


@router.get("/report")
async def attendance_report(
    kg_id: str,
    date_from: date,
    date_to: date,
    group_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    records = await attendance_service.get_report(db, kg_id, date_from, date_to, group_id)
    return [
        {
            "id": str(r.id),
            "child_id": str(r.child_id),
            "date": str(r.date),
            "status": r.status,
            "note": r.note,
        }
        for r in records
    ]
