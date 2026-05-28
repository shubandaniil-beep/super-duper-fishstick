import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import InviteCode


async def generate(db: AsyncSession, kg_id: str, role: str, user_id: Optional[str] = None) -> str:
    code = "".join(random.choices(string.digits, k=4))
    invite = InviteCode(
        code=code,
        kg_id=kg_id,
        role=role,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    await db.commit()
    return code


async def verify_and_use(db: AsyncSession, code: str) -> Optional[InviteCode]:
    result = await db.execute(
        select(InviteCode).where(
            InviteCode.code == code,
            InviteCode.is_used == False,
            InviteCode.expires_at > datetime.now(timezone.utc),
        )
    )
    invite = result.scalar_one_or_none()
    if invite:
        invite.is_used = True
        await db.commit()
    return invite


async def get_session(db: AsyncSession, telegram_id: int):
    from app.db.models import TelegramSession
    result = await db.execute(
        select(TelegramSession).where(TelegramSession.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def set_session(db: AsyncSession, telegram_id: int, state: str, data: dict = None):
    from app.db.models import TelegramSession
    session = await get_session(db, telegram_id)
    if session:
        session.state = state
        session.state_data = data or {}
    else:
        session = TelegramSession(telegram_id=telegram_id, state=state, state_data=data or {})
        db.add(session)
    await db.commit()


async def clear_session(db: AsyncSession, telegram_id: int):
    from app.db.models import TelegramSession
    session = await get_session(db, telegram_id)
    if session:
        session.state = None
        session.state_data = {}
        await db.commit()
