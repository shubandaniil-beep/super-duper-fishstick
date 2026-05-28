from telegram import Update
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, children_service, groups_service, invite_service


async def start_message_to_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_id = query.from_user.id

    async with AsyncSessionLocal() as db:
        parent = await users_service.get_by_telegram_id(db, tg_id)
        children = await children_service.get_by_parent(db, str(parent.id))
        if not children:
            await query.message.reply_text("Нет привязанных детей.")
            return
        child = children[0]
        group = await groups_service.get(db, str(child.group_id))
        teacher = await users_service.get_by_id(db, str(group.teacher_id)) if group.teacher_id else None
        if not teacher:
            await query.message.reply_text("Воспитатель не назначен.")
            return

        await invite_service.set_session(db, tg_id, "messaging_teacher", {
            "teacher_id": str(teacher.id),
            "child_id": str(child.id),
        })

    await query.edit_message_text(
        f"✉️ Напишите сообщение воспитателю {teacher.full_name}.\nОно будет доставлено в Telegram:"
    )


async def handle_parent_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user=None):
    tg_id = update.effective_user.id

    async with AsyncSessionLocal() as db:
        if user is None:
            user = await users_service.get_by_telegram_id(db, tg_id)
        session = await invite_service.get_session(db, tg_id)
        if not session or session.state != "messaging_teacher":
            return

        data = session.state_data or {}
        teacher = await users_service.get_by_id(db, data.get("teacher_id", ""))
        child = await children_service.get(db, data.get("child_id", ""))

        if teacher and teacher.telegram_id:
            from app.bot.main import get_bot
            bot = get_bot()
            try:
                await bot.send_message(
                    chat_id=teacher.telegram_id,
                    text=(
                        f"✉️ *Сообщение от родителя*\n"
                        f"👤 {user.full_name}\n"
                        f"👶 Ребёнок: {child.first_name} {child.last_name if child else ''}\n\n"
                        f"📩 {update.message.text}"
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

        await invite_service.clear_session(db, tg_id)

    await update.message.reply_text("✅ Сообщение отправлено воспитателю!")
