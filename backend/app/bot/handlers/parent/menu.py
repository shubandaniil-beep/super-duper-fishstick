from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, children_service, menu_service

MEAL_LABELS = {
    "breakfast": "🌅 Завтрак",
    "lunch": "🌞 Обед",
    "snack": "☕ Полдник",
    "dinner": "🌙 Ужин",
}


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, day_offset: int = 0):
    query = update.callback_query
    if query:
        await query.answer()
    tg_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        parent = await users_service.get_by_telegram_id(db, tg_id)
        children = await children_service.get_by_parent(db, str(parent.id))
        if not children:
            msg = query.message if query else update.message
            await msg.reply_text("Нет привязанных детей.")
            return
        child = children[0]
        target_date = date.today() + timedelta(days=day_offset)
        items = await menu_service.get_by_date(db, str(child.kindergarten_id), target_date)

    text = f"🍽️ Меню на {target_date.strftime('%d.%m.%Y')}\n\n"
    if not items:
        text += "Меню не опубликовано."
    else:
        for item in items:
            label = MEAL_LABELS.get(item.meal_type, item.meal_type)
            text += f"{label}\n   {item.description}"
            if item.calories:
                text += f" ({item.calories} ккал)"
            text += "\n\n"

    keyboard = [[
        InlineKeyboardButton("◀️ Вчера", callback_data=f"menu_day_{day_offset - 1}"),
        InlineKeyboardButton("▶️ Завтра", callback_data=f"menu_day_{day_offset + 1}"),
    ]]

    if query:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def menu_day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    offset = int(query.data.replace("menu_day_", ""))
    await show_menu(update, context, day_offset=offset)
