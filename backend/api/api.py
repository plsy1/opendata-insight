from fastapi import APIRouter
from .router import prowlarr,qbittorrent,javbus,avbase,auth,feed,fanza,emby,javtrailers,statistic,fc2
from .router import system
from core.auth import *

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(prowlarr.router, prefix="/prowlarr", tags=["prowlarr"])
api_router.include_router(qbittorrent.router, prefix="/downloader", tags=["downloader"])
# api_router.include_router(javbus.router, prefix="/javbus", tags=["discover"])
api_router.include_router(avbase.router, prefix="/avbase", tags=["avbase"])
api_router.include_router(fanza.router, prefix="/fanza", tags=["fanza"])
api_router.include_router(emby.router, prefix="/emby", tags=["emby"])
api_router.include_router(javtrailers.router, prefix="/javtrailers", tags=["javtrailers"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(statistic.router, prefix="/statistic", tags=["statistic"])
api_router.include_router(fc2.router, prefix="/fc2", tags=["fc2"])