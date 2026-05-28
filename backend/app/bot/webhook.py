"""Webhook mode — обрабатывает входящие update от Telegram."""
from telegram import Update
from app.bot.main import get_application


async def process_update(data: dict):
    app = await get_application()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
