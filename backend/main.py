import asyncio
import os
from app.api.main import app  # noqa: F401 — export for uvicorn
from app.bot.main import start_bot


async def main():
    """Entry point: run FastAPI + Telegram bot concurrently."""
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        start_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
