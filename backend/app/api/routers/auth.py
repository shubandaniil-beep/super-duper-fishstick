from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "name": user.full_name,
            "role": user.role,
            "kindergarten_id": str(user.kindergarten_id) if user.kindergarten_id else None,
        },
    }
