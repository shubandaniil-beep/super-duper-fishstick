from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, children_service, attendance_service, groups_service

STATUS_MAP = {
    "present": "✅ Присутствует",
    "absent_sick": "🤒 Болеет",
    "absent_vacation": "✈️ В отпуске",
    "absent_other": "❓ Отсутствует",
    None: "⏳ Ещё не отмечен",
}


async def show_child_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    tg_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        parent = await users_service.get_by_telegram_id(db, tg_id)
        children = await children_service.get_by_parent(db, str(parent.id))

    if not children:
        msg = query.message if query else update.message
        await msg.reply_text("У вас нет привязанных детей. Обратитесь к администратору.")
        return

    if len(children) > 1:
        keyboard = [[InlineKeyboardButton(
            f"{c.first_name} {c.last_name}", callback_data=f"child_status_{c.id}"
        )] for c in children]
        msg = query.message if query else update.message
        await msg.reply_text("Выберите ребёнка:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await _show_single_child(update, children[0].id)


async def show_child_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    child_id = query.data.replace("child_status_", "")
    await _show_single_child(update, child_id)


async def _show_single_child(update: Update, child_id: str):
    query = update.callback_query

    async with AsyncSessionLocal() as db:
        child = await children_service.get(db, child_id)
        today_att = await attendance_service.get_today(db, child_id)
        group = await groups_service.get(db, str(child.group_id))
        teacher = await users_service.get_by_id(db, str(group.teacher_id)) if group.teacher_id else None

    status = today_att.status if today_att else None
    text = (
        f"👶 *{child.first_name} {child.last_name}*\n"
        f"Группа: {group.name}\n\n"
        f"📅 Сегодня, {date.today().strftime('%d.%m.%Y')}\n"
        f"Статус: {STATUS_MAP[status]}\n\n"
        f"👩‍🏫 Воспитатель: {teacher.full_name if teacher else 'не указан'}"
    )
    keyboard = [[
        InlineKeyboardButton("📊 Посещаемость за месяц", callback_data=f"att_month_{child_id}")
    ]]

    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_attendance_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    child_id = query.data.replace("att_month_", "")

    today = date.today()
    async with AsyncSessionLocal() as db:
        child = await children_service.get(db, child_id)
        records = await attendance_service.get_month(db, child_id, today.year, today.month)

    status_icons = {"present": "✅", "absent_sick": "🤒", "absent_vacation": "✈️", "absent_other": "❓"}
    months_ru = ["", "январь", "февраль", "март", "апрель", "май", "июнь",
                 "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

    text = f"📊 Посещаемость — {months_ru[today.month].capitalize()} {today.year}\n{child.first_name} {child.last_name}\n\n"
    for r in records:
        icon = status_icons.get(r.status, "—")
        text += f"{icon} {r.date.strftime('%d.%m')} — {r.status}\n"

    present = sum(1 for r in records if r.status == "present")
    text += f"\nИтог: {present}/{len(records)} дней"
    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data=f"child_status_{child_id}")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
