from fastapi import APIRouter
from . import (
    prowlarr,
    qbittorrent,
    avbase,
    auth,
    feed,
    fanza,
    emby,
    fc2,
    system,
    background_task,
    statistic,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(prowlarr.router, prefix="/prowlarr", tags=["prowlarr"])
api_router.include_router(qbittorrent.router, prefix="/downloader", tags=["downloader"])
api_router.include_router(avbase.router, prefix="/avbase", tags=["avbase"])
api_router.include_router(fanza.router, prefix="/fanza", tags=["fanza"])
api_router.include_router(emby.router, prefix="/emby", tags=["emby"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(
    background_task.router, prefix="/background_task", tags=["background_task"]
)
api_router.include_router(fc2.router, prefix="/fc2", tags=["fc2"])
api_router.include_router(statistic.router, prefix="/statistic", tags=["statistic"])
