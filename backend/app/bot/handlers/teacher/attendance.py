from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, groups_service, children_service, attendance_service
from app.schemas.attendance import AttendanceBulkCreate, AttendanceCreate


STATUS_LABELS = {
    "present": "✅",
    "absent_sick": "🤒",
    "absent_vacation": "✈️",
    "absent_other": "❓",
}

STATUS_TEXT = {
    "absent_sick": "🤒 заболел(а)",
    "absent_vacation": "✈️ в отпуске",
    "absent_other": "❓ отсутствует по иной причине",
}


async def show_attendance_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    async with AsyncSessionLocal() as db:
        teacher = await users_service.get_by_telegram_id(db, tg_id)
        if not teacher:
            return
        group = await groups_service.get_by_teacher(db, str(teacher.id))
        if not group:
            msg = update.message or update.callback_query.message
            await msg.reply_text("У вас нет назначенной группы. Обратитесь к администратору.")
            return
        children = await children_service.get_by_group(db, str(group.id))

    context.user_data["attendance"] = {str(c.id): None for c in children}
    context.user_data["children_map"] = {str(c.id): f"{c.last_name} {c.first_name}" for c in children}
    context.user_data["group_name"] = group.name
    context.user_data["group_id"] = str(group.id)

    keyboard = _build_attendance_keyboard(context)
    text = f"📋 Посещаемость — {group.name}\n📅 {date.today().strftime('%d.%m.%Y')}\n\nОтметьте каждого ребёнка:"

    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def _build_attendance_keyboard(context: ContextTypes.DEFAULT_TYPE):
    att = context.user_data.get("attendance", {})
    children_map = context.user_data.get("children_map", {})
    keyboard = []
    for child_id, name in children_map.items():
        chosen = att.get(child_id)
        label = f"{'✓ ' if chosen else ''}{name}"
        keyboard.append([InlineKeyboardButton(label, callback_data="noop")])
        row = []
        for status, emoji in STATUS_LABELS.items():
            mark = "【" + emoji + "】" if chosen == status else emoji
            row.append(InlineKeyboardButton(mark, callback_data=f"att_{child_id}_{status}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💾 Сохранить", callback_data="att_save")])
    return keyboard


async def attendance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "att_save":
        await save_attendance(update, context)
        return

    if query.data == "noop":
        return

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        return
    _, child_id, status = parts
    context.user_data["attendance"][child_id] = status

    keyboard = _build_attendance_keyboard(context)
    group_name = context.user_data.get("group_name", "")
    text = f"📋 Посещаемость — {group_name}\n📅 {date.today().strftime('%d.%m.%Y')}\n\nОтметьте каждого ребёнка:"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def save_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tg_id = query.from_user.id
    att_data = context.user_data.get("attendance", {})
    group_id = context.user_data.get("group_id", "")

    async with AsyncSessionLocal() as db:
        teacher = await users_service.get_by_telegram_id(db, tg_id)
        records = [
            AttendanceCreate(child_id=child_id, date=date.today(), status=status)
            for child_id, status in att_data.items()
            if status
        ]
        if records:
            bulk = AttendanceBulkCreate(group_id=group_id, date=date.today(), records=records)
            await attendance_service.bulk_mark(db, bulk, marked_by=str(teacher.id))

        # Notify parents of absent children
        for child_id, status in att_data.items():
            if status and status != "present":
                await _notify_parent_absent(db, child_id, status)

    present = sum(1 for s in att_data.values() if s == "present")
    total = len(att_data)
    await query.edit_message_text(
        f"✅ Посещаемость сохранена!\n\n"
        f"Присутствует: {present}/{total}\n"
        f"Отсутствует: {total - present}"
    )


async def _notify_parent_absent(db, child_id: str, status: str):
    from app.bot.main import get_bot
    child = await children_service.get(db, child_id)
    if not child:
        return
    parents = await users_service.get_parents(db, child_id)
    bot = get_bot()
    for parent in parents:
        if parent.telegram_id:
            try:
                await bot.send_message(
                    chat_id=parent.telegram_id,
                    text=(
                        f"ℹ️ Сегодня ({date.today().strftime('%d.%m.%Y')}) "
                        f"{child.first_name} отмечен(а) как {STATUS_TEXT.get(status, status)}.\n"
                        f"Если это ошибка — обратитесь к воспитателю."
                    ),
                )
            except Exception:
                pass


async def show_children_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_id = query.from_user.id

    async with AsyncSessionLocal() as db:
        teacher = await users_service.get_by_telegram_id(db, tg_id)
        group = await groups_service.get_by_teacher(db, str(teacher.id))
        if not group:
            await query.message.reply_text("У вас нет назначенной группы.")
            return
        children = await children_service.get_by_group(db, str(group.id))

    keyboard = [
        [InlineKeyboardButton(f"👤 {c.last_name} {c.first_name}", callback_data=f"child_info_{c.id}")]
        for c in children
    ]
    await query.edit_message_text(
        f"👶 Дети — {group.name} ({len(children)} чел.)\n\nНажмите на имя для подробной информации:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def child_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    child_id = query.data.replace("child_info_", "")

    async with AsyncSessionLocal() as db:
        child = await children_service.get(db, child_id)
        parents = await users_service.get_parents(db, child_id)
        from app.services import medical_service
        records = await medical_service.get_by_child(db, child_id)

    if not child:
        await query.message.reply_text("Ребёнок не найден.")
        return

    age = (date.today() - child.birth_date).days // 365
    parents_text = "\n".join(
        f"  👤 {p.full_name}" + (f" ({p.phone})" if p.phone else "") for p in parents
    ) or "  не указаны"

    text = (
        f"👤 *{child.last_name} {child.first_name}*\n"
        f"🎂 Дата рождения: {child.birth_date.strftime('%d.%m.%Y')} ({age} лет)\n\n"
        f"👨‍👩‍👦 Родители:\n{parents_text}\n\n"
        f"⚕️ Аллергии: {child.allergies or 'нет'}\n"
        f"📝 Медзаметки: {child.medical_notes or 'нет'}"
    )
    keyboard = [
        [InlineKeyboardButton("💊 Медкарта", callback_data=f"med_{child_id}")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_children")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
