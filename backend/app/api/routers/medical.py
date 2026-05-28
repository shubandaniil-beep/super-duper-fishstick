from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.medical import MedicalRecordCreate, MedicalRecordOut
from app.services import medical_service
from app.api.dependencies import get_current_teacher

router = APIRouter(prefix="/medical", tags=["medical"])


@router.get("/{child_id}", response_model=List[MedicalRecordOut])
async def get_medical_records(
    child_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await medical_service.get_by_child(db, child_id)


@router.post("/", response_model=MedicalRecordOut)
async def create_medical_record(
    data: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_teacher),
):
    return await medical_service.create(db, data)
