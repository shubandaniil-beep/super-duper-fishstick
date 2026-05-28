from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, groups_service, schedule_service

DAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
MONTHS_RU = ["", "янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]


async def show_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE, week_offset: int = 0):
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
    tg_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        teacher = await users_service.get_by_telegram_id(db, tg_id)
        group = await groups_service.get_by_teacher(db, str(teacher.id))
        if not group:
            msg = query.message if query else update.message
            await msg.reply_text("У вас нет назначенной группы.")
            return
        items = await schedule_service.get_by_group(db, str(group.id))

    monday = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=week_offset)
    text = f"📅 Расписание — {group.name}\n\n"

    for day_idx in range(5):
        day_date = monday + timedelta(days=day_idx)
        day_items = [s for s in items if s.day_of_week == day_idx + 1]
        text += f"*{DAYS_RU[day_idx]}, {day_date.day} {MONTHS_RU[day_date.month]}*\n"
        if day_items:
            for item in sorted(day_items, key=lambda x: x.time_start):
                text += f"  {item.time_start.strftime('%H:%M')}–{item.time_end.strftime('%H:%M')}  {item.subject}\n"
        else:
            text += "  нет занятий\n"
        text += "\n"

    keyboard = [[
        InlineKeyboardButton("◀️ Прошлая", callback_data=f"schedule_{week_offset - 1}"),
        InlineKeyboardButton("▶️ Следующая", callback_data=f"schedule_{week_offset + 1}"),
    ]]

    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    offset = int(query.data.replace("schedule_", ""))
    await show_schedule(update, context, week_offset=offset)
