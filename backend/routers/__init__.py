from fastapi import APIRouter, Depends
from . import (
    prowlarr,
    qbittorrent,
    avbase,
    auth,
    fanza,
    emby,
    fc2,
    schedule,
    subscribe,
    system,
    statistic,
)

from .dependencies.auth_dependencies import token_interceptor

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

protected_routers = [
    (subscribe.router, "/feed", ["feed"]),
    (prowlarr.router, "/prowlarr", ["prowlarr"]),
    (qbittorrent.router, "/downloader", ["downloader"]),
    (avbase.router, "/avbase", ["avbase"]),
    (fanza.router, "/fanza", ["fanza"]),
    (emby.router, "/emby", ["emby"]),
    (schedule.router, "/background_task", ["background_task"]),
    (fc2.router, "/fc2", ["fc2"]),
    (statistic.router, "/statistic", ["statistic"]),
]

for r, prefix, tags in protected_routers:
    api_router.include_router(
        r, prefix=prefix, tags=tags, dependencies=[Depends(token_interceptor)]
    )
