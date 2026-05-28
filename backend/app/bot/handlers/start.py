from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, invite_service


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    async with AsyncSessionLocal() as db:
        user = await users_service.get_by_telegram_id(db, tg_id)

    if user:
        await show_main_menu(update, user)
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать в KinderManager!\n\n"
            "Введите 4-значный код регистрации, который вам выдал администратор садика:"
        )
        context.user_data["state"] = "awaiting_invite_code"


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    if state == "awaiting_invite_code":
        await handle_invite_code(update, context)
        return

    tg_id = update.effective_user.id
    async with AsyncSessionLocal() as db:
        session = await invite_service.get_session(db, tg_id)
        user = await users_service.get_by_telegram_id(db, tg_id)

    if not user:
        await update.message.reply_text("Пожалуйста, введите код регистрации или напишите /start")
        return

    if session and session.state == "messaging_teacher":
        from app.bot.handlers.parent.message import handle_parent_message
        await handle_parent_message(update, context, user)
        return

    await show_main_menu(update, user)


async def handle_invite_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    tg_id = update.effective_user.id
    tg_username = update.effective_user.username

    async with AsyncSessionLocal() as db:
        invite = await invite_service.verify_and_use(db, code)
        if not invite:
            await update.message.reply_text(
                "❌ Код недействителен или истёк срок.\nОбратитесь к администратору для получения нового кода."
            )
            return

        if invite.user_id:
            await users_service.link_telegram(db, invite.user_id, tg_id, tg_username)
            user = await users_service.get_by_id(db, invite.user_id)
        else:
            from app.schemas.users import UserCreate
            user = await users_service.create(db, UserCreate(
                kindergarten_id=invite.kg_id,
                role=invite.role,
                full_name=update.effective_user.full_name,
                telegram_id=tg_id,
            ))

    context.user_data["state"] = None
    await update.message.reply_text(f"✅ Вы успешно зарегистрированы как {_role_name(invite.role)}!")
    await show_main_menu(update, user)


async def show_main_menu(update: Update, user):
    if user.role == "teacher":
        keyboard = [
            [InlineKeyboardButton("📋 Посещаемость", callback_data="menu_attendance")],
            [InlineKeyboardButton("📰 Новости / Фото", callback_data="menu_posts")],
            [InlineKeyboardButton("📅 Расписание", callback_data="menu_schedule")],
            [InlineKeyboardButton("👶 Мои дети", callback_data="menu_children")],
        ]
        text = f"👩‍🏫 Здравствуйте, {user.full_name}!\nВыберите раздел:"
    elif user.role == "parent":
        keyboard = [
            [InlineKeyboardButton("👶 Мой ребёнок", callback_data="menu_child_status")],
            [InlineKeyboardButton("📰 Новости группы", callback_data="menu_news")],
            [InlineKeyboardButton("📅 Расписание", callback_data="menu_schedule")],
            [InlineKeyboardButton("🍽️ Меню", callback_data="menu_food")],
            [InlineKeyboardButton("✉️ Написать воспитателю", callback_data="menu_message")],
        ]
        text = f"👋 Здравствуйте, {user.full_name}!\nВыберите раздел:"
    else:
        text = f"Роль '{user.role}' работает через веб-панель."
        keyboard = []

    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if msg:
        await msg.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None)


def _role_name(role: str) -> str:
    return {"teacher": "воспитатель", "parent": "родитель"}.get(role, role)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_id = query.from_user.id

    async with AsyncSessionLocal() as db:
        user = await users_service.get_by_telegram_id(db, tg_id)

    if not user:
        await query.message.reply_text("Сначала пройдите регистрацию через /start")
        return

    data = query.data
    if data == "menu_attendance":
        from app.bot.handlers.teacher.attendance import show_attendance_form
        await show_attendance_form(update, context)
    elif data == "menu_posts":
        from app.bot.handlers.teacher.posts import show_post_menu
        await show_post_menu(update, context)
    elif data == "menu_schedule":
        from app.bot.handlers.teacher.schedule import show_schedule
        await show_schedule(update, context)
    elif data == "menu_children":
        from app.bot.handlers.teacher.attendance import show_children_list
        await show_children_list(update, context)
    elif data == "menu_child_status":
        from app.bot.handlers.parent.child import show_child_status
        await show_child_status(update, context)
    elif data == "menu_news":
        from app.bot.handlers.parent.news import show_news_feed
        await show_news_feed(update, context)
    elif data == "menu_food":
        from app.bot.handlers.parent.menu import show_menu
        await show_menu(update, context)
    elif data == "menu_message":
        from app.bot.handlers.parent.message import start_message_to_teacher
        await start_message_to_teacher(update, context)
    elif data == "open_attendance":
        from app.bot.handlers.teacher.attendance import show_attendance_form
        await show_attendance_form(update, context)
