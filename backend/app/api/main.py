from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import (
    auth, kindergartens, groups, children, users,
    attendance, schedule, menu, posts, medical, stats, invites,
)

app = FastAPI(title="KinderManager API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(kindergartens.router, prefix=PREFIX)
app.include_router(groups.router, prefix=PREFIX)
app.include_router(children.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(attendance.router, prefix=PREFIX)
app.include_router(schedule.router, prefix=PREFIX)
app.include_router(menu.router, prefix=PREFIX)
app.include_router(posts.router, prefix=PREFIX)
app.include_router(medical.router, prefix=PREFIX)
app.include_router(stats.router, prefix=PREFIX)
app.include_router(invites.router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}


async def start_api():
    import uvicorn
    from app.core.config import settings
    port = 8000
    config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()
