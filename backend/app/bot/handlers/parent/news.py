from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from app.db.base import AsyncSessionLocal
from app.services import users_service, children_service, posts_service


async def show_news_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        posts = await posts_service.get_feed(db, kg_id=str(child.kindergarten_id),
                                             group_id=str(child.group_id), limit=10)

    msg = query.message if query else update.message

    if not posts:
        await msg.reply_text("📭 Новостей пока нет.")
        return

    for post in posts:
        text = f"📰 *{post.title or 'Новость'}*\n{post.created_at.strftime('%d.%m.%Y')}"
        if post.content:
            text += f"\n\n{post.content}"

        if post.media_urls:
            media = [InputMediaPhoto(url) for url in post.media_urls[:10]]
            await msg.reply_media_group(media=media)

        await msg.reply_text(text, parse_mode="Markdown")
