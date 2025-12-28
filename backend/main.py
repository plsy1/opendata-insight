import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import _config
from utils.logs import LOGGING_CONFIG
from database import initDatabase
from services.auth import initUser
from modules.scheduler import init_scheduler_service
from modules.playwright import init_playwright_service
from modules.notification.telegram import init_telegram_bot
from modules.downloader.qbittorrent import init_qb


def Init():
    initDatabase()
    initUser()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Init()
    scheduler = init_scheduler_service()
    playwright = await init_playwright_service()
    tgbot = await init_telegram_bot(
        _config.get("TELEGRAM_TOKEN", ""), _config.get("TELEGRAM_CHAT_ID", "")
    )
    qb_client = await init_qb()
    initRouter()

    try:
        yield
    finally:
        await tgbot.shutdown()
        await playwright.stop()
        scheduler.shutdown()


App = FastAPI(lifespan=lifespan)

App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Config = uvicorn.Config(
    App, host="0.0.0.0", port=8964, reload=True, log_config=LOGGING_CONFIG
)

Server = uvicorn.Server(Config)


def initRouter():
    from routers import api_router

    App.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    Server.run()
