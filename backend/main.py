import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import _config
from utils.logs import LOGGING_CONFIG
from database import init_database
from services.auth import init_user

from modules.scheduler import init_scheduler_service, shutdown_scheduler_service
from modules.playwright import init_playwright_service, shutdown_playwright_service
from modules.notification.telegram import init_telegram_bot, shutdown_telegram_bot
from modules.downloader.qbittorrent import init_qb, shutdown_qb
from modules.metadata.prowlarr import init_prowlarr, shutdown_prowlarr
from modules.mediaServer.emby import init_emby_service, shutdown_emby_service


def init_environments():
    init_database()
    init_user()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_environments()

    await init_scheduler_service()
    await init_playwright_service()

    await init_telegram_bot(
        _config.get("TELEGRAM_TOKEN", ""), _config.get("TELEGRAM_CHAT_ID", "")
    )

    await init_qb(
        _config.get("QB_URL"),
        username=_config.get("QB_USERNAME"),
        password=_config.get("QB_PASSWORD"),
    )

    await init_prowlarr(
        _config.get("PROWLARR_URL", ""), _config.get("PROWLARR_KEY", "")
    )

    await init_emby_service(_config.get("EMBY_URL"), _config.get("EMBY_API_KEY"))

    init_router()

    try:
        yield
    finally:
        await shutdown_emby_service()
        await shutdown_prowlarr()
        await shutdown_qb()
        await shutdown_telegram_bot()
        await shutdown_playwright_service()
        await shutdown_scheduler_service()


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


def init_router():
    from routers import api_router

    App.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    Server.run()
