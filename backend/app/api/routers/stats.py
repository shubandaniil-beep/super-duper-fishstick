from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db.base import get_db
from app.services import children_service, attendance_service, users_service, groups_service
from app.api.dependencies import get_current_admin
from app.db.models import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
async def get_dashboard_stats(
    kg_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    today = date.today()
    return {
        "total_children": await children_service.count(db, kg_id),
        "present_today": await attendance_service.count_present(db, kg_id, today),
        "absent_today": await attendance_service.count_absent(db, kg_id, today),
        "total_teachers": await users_service.count_by_role(db, kg_id, "teacher"),
        "groups_count": await groups_service.count(db, kg_id),
        "attendance_percent": await attendance_service.percent_this_month(db, kg_id),
    }
