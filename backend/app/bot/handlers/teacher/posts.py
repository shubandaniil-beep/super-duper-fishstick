from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, groups_service, posts_service
from app.schemas.posts import PostCreate


async def show_post_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Фото из группы", callback_data="post_photo")],
        [InlineKeyboardButton("📢 Объявление", callback_data="post_announcement")],
        [InlineKeyboardButton("📰 Новость", callback_data="post_news")],
    ]
    msg = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Что хотите опубликовать?", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text("Что хотите опубликовать?", reply_markup=InlineKeyboardMarkup(keyboard))


async def post_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    post_type = query.data.replace("post_", "")
    context.user_data["post_type"] = post_type
    context.user_data["photos"] = []
    context.user_data["post_caption"] = ""

    if post_type == "photo":
        context.user_data["state"] = "awaiting_photos"
        await query.edit_message_text("📸 Отправьте фото (можно несколько, до 10 шт):")
    else:
        context.user_data["state"] = "awaiting_post_title"
        await query.edit_message_text("✏️ Введите заголовок:")


async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "awaiting_photos":
        return
    photo = update.message.photo[-1]
    photos = context.user_data.setdefault("photos", [])
    photos.append(photo.file_id)

    keyboard = [
        [InlineKeyboardButton("📸 Добавить ещё", callback_data="photo_more")],
        [InlineKeyboardButton("✅ Готово — без подписи", callback_data="photo_done_no_caption")],
        [InlineKeyboardButton("✏️ Добавить подпись", callback_data="photo_add_caption")],
    ]
    await update.message.reply_text(
        f"Добавлено фото: {len(photos)}\nДобавить ещё или завершить?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def photo_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "photo_more":
        context.user_data["state"] = "awaiting_photos"
        await query.edit_message_text("📸 Отправьте следующее фото:")
    elif query.data == "photo_add_caption":
        context.user_data["state"] = "awaiting_caption"
        await query.edit_message_text("✏️ Введите подпись к фото:")
    elif query.data == "photo_done_no_caption":
        await ask_audience(query, context)
    elif query.data in ("audience_all", "audience_group"):
        await publish_post(query, context, target=query.data.replace("audience_", ""))


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")

    if state == "awaiting_caption":
        context.user_data["post_caption"] = update.message.text
        context.user_data["state"] = None
        await ask_audience_msg(update.message, context)

    elif state == "awaiting_post_title":
        context.user_data["post_title"] = update.message.text
        context.user_data["state"] = "awaiting_post_content"
        await update.message.reply_text("✏️ Введите текст сообщения:")

    elif state == "awaiting_post_content":
        context.user_data["post_content"] = update.message.text
        context.user_data["state"] = None
        await ask_audience_msg(update.message, context)


async def ask_audience(query, context):
    keyboard = [
        [InlineKeyboardButton("🏫 Всему садику", callback_data="audience_all")],
        [InlineKeyboardButton("👥 Только моей группе", callback_data="audience_group")],
    ]
    await query.edit_message_text("Кому отправить?", reply_markup=InlineKeyboardMarkup(keyboard))


async def ask_audience_msg(message, context):
    keyboard = [
        [InlineKeyboardButton("🏫 Всему садику", callback_data="audience_all")],
        [InlineKeyboardButton("👥 Только моей группе", callback_data="audience_group")],
    ]
    await message.reply_text("Кому отправить?", reply_markup=InlineKeyboardMarkup(keyboard))


async def publish_post(query, context: ContextTypes.DEFAULT_TYPE, target: str):
    tg_id = query.from_user.id
    post_type = context.user_data.get("post_type", "news")

    async with AsyncSessionLocal() as db:
        teacher = await users_service.get_by_telegram_id(db, tg_id)
        group = await groups_service.get_by_teacher(db, str(teacher.id))
        post_data = PostCreate(
            kg_id=teacher.kindergarten_id,
            group_id=str(group.id) if target == "group" else None,
            type=post_type,
            title=context.user_data.get("post_title"),
            content=context.user_data.get("post_caption") or context.user_data.get("post_content"),
            media_urls=context.user_data.get("photos") or [],
        )
        post = await posts_service.create(db, post_data, author_id=str(teacher.id))

        recipients = await users_service.get_parents_for_target(
            db, kg_id=str(teacher.kindergarten_id),
            group_id=str(group.id) if target == "group" else None,
        )

        from app.bot.main import get_bot
        bot = get_bot()
        sent = 0
        for parent in recipients:
            if parent.telegram_id:
                try:
                    if post.media_urls:
                        media = [InputMediaPhoto(fid) for fid in post.media_urls[:10]]
                        await bot.send_media_group(chat_id=parent.telegram_id, media=media)
                    caption = post.content or post.title or ""
                    if caption:
                        await bot.send_message(chat_id=parent.telegram_id, text=caption)
                    sent += 1
                except Exception:
                    pass

        await posts_service.mark_sent(db, str(post.id))

    context.user_data.clear()
    await query.edit_message_text(f"✅ Опубликовано!\nОтправлено родителям: {sent}")
