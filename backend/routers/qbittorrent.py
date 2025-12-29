from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Body,
    Response,
    status,
)

from pathlib import Path
from sqlalchemy.orm import Session
from config import _config
from database import get_db
from services.auth import tokenInterceptor
from services.subscribe import *
from services.telegram import *


router = APIRouter()


@router.get(
    "/get_downloading_torrents",
)
async def get(isValid: str = Depends(tokenInterceptor)):

    from modules.downloader.qbittorrent import _qb_instance

    return await _qb_instance.get_downloading_torrents()


@router.post("/delete_torrent")
async def delete(
    torrent_hash: str = Body(...),
    delete_files: bool = Body(True),
    isValid: str = Depends(tokenInterceptor),
):

    from modules.downloader.qbittorrent import _qb_instance

    try:
        await _qb_instance.delete_torrent(torrent_hash, delete_files=delete_files)
        return {
            "status": "success",
            "hash": torrent_hash,
            "deleted_files": delete_files,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/add_torrent_url")
async def add_torrent_url(
    work_id: str,
    download_link: str,
    save_path: str,
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    try:

        save_path = (
            Path(save_path) if save_path else Path(_config.get("DOWNLOAD_PATH", ""))
        )

        records = db.query(MovieData).filter(MovieData.work_id == work_id).first()

        if records:
            movie_out = MovieDataOut.model_validate(records)

            top_names_list = [
                cast["name"] for cast in movie_out.casts if cast.get("name")
            ][:3]

            top_names = ", ".join(top_names_list)

            save_path = save_path / top_names

        from modules.downloader.qbittorrent import _qb_instance

        success = await _qb_instance.add_torrent_url(download_link, save_path)

        if success and work_id:
            movie_subscribe_service(db, MovieFeedOperation.MARK_DOWNLOADED, work_id)
            await send_movie_download_message_by_work_id(
                work_id, DownloadStatus.START_DOWNLOAD
            )

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=400, detail="Failed to add torrent")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
