from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.base import AsyncSessionLocal
from app.services import users_service, groups_service, attendance_service

scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
_bot = None


def setup_scheduler(bot):
    global _bot
    _bot = bot
    scheduler.add_job(remind_teachers_attendance, "cron", hour=8, minute=30,
                      day_of_week="mon-fri", id="remind_attendance")
    scheduler.start()


async def remind_teachers_attendance():
    if not _bot:
        return
    async with AsyncSessionLocal() as db:
        teachers = await users_service.get_all_teachers(db)
        for teacher in teachers:
            if not teacher.telegram_id:
                continue
            group = await groups_service.get_by_teacher(db, str(teacher.id))
            if not group:
                continue
            already_marked = await attendance_service.is_marked_today(db, str(group.id))
            if already_marked:
                continue
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton("📋 Отметить посещаемость", callback_data="open_attendance")]]
            try:
                await _bot.send_message(
                    chat_id=teacher.telegram_id,
                    text=f"⏰ Доброе утро!\nНе забудьте отметить посещаемость группы *{group.name}*",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
            except Exception:
                pass
