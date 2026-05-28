from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.config import settings

_bot_app: Application = None


def get_bot():
    return _bot_app.bot if _bot_app else None


async def start_bot():
    global _bot_app

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    _bot_app = app

    from app.bot.handlers.start import (
        start_handler, text_handler, main_menu_callback
    )
    from app.bot.handlers.teacher.attendance import (
        attendance_callback, child_info_callback
    )
    from app.bot.handlers.teacher.posts import (
        post_type_callback, photo_action_callback, handle_photo_upload, handle_text_input
    )
    from app.bot.handlers.teacher.schedule import schedule_callback
    from app.bot.handlers.parent.child import show_child_by_id, show_attendance_month
    from app.bot.handlers.parent.menu import menu_day_callback
    from app.bot.scheduled import setup_scheduler

    # Commands
    app.add_handler(CommandHandler("start", start_handler))

    # Photo uploads
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_upload))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _combined_text_handler))

    # Callbacks
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern=r"^menu_"))
    app.add_handler(CallbackQueryHandler(attendance_callback, pattern=r"^att_"))
    app.add_handler(CallbackQueryHandler(child_info_callback, pattern=r"^child_info_"))
    app.add_handler(CallbackQueryHandler(show_child_by_id, pattern=r"^child_status_"))
    app.add_handler(CallbackQueryHandler(show_attendance_month, pattern=r"^att_month_"))
    app.add_handler(CallbackQueryHandler(post_type_callback, pattern=r"^post_"))
    app.add_handler(CallbackQueryHandler(photo_action_callback, pattern=r"^photo_"))
    app.add_handler(CallbackQueryHandler(photo_action_callback, pattern=r"^audience_"))
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern=r"^schedule_"))
    app.add_handler(CallbackQueryHandler(menu_day_callback, pattern=r"^menu_day_"))
    app.add_handler(CallbackQueryHandler(_noop_callback, pattern=r"^noop$"))

    setup_scheduler(app.bot)

    if settings.ENVIRONMENT == "production" and settings.WEBHOOK_URL:
        await app.bot.set_webhook(url=f"{settings.WEBHOOK_URL}/webhook")
        async with app:
            await app.start()
            # Keep running — webhook mode handled by FastAPI
            import asyncio
            await asyncio.Event().wait()
    else:
        async with app:
            await app.start()
            await app.updater.start_polling()
            import asyncio
            await asyncio.Event().wait()


async def _combined_text_handler(update: Update, context):
    from app.bot.handlers.teacher.posts import handle_text_input as posts_text
    from app.bot.handlers.start import text_handler

    state = context.user_data.get("state", "")
    if state in ("awaiting_caption", "awaiting_post_title", "awaiting_post_content"):
        await posts_text(update, context)
    else:
        await text_handler(update, context)


async def _noop_callback(update, context):
    await update.callback_query.answer()
