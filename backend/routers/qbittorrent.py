from fastapi import (
    HTTPException,
    Query,
    UploadFile,
    File,
    APIRouter,
    Depends,
    Body,
    Response,
    status,
)

from pathlib import Path
from io import BytesIO
from modules.downloader.qbittorrent import QB
from services.auth import tokenInterceptor
from config import _config
from modules.metadata.avbase import *
from database import get_db
from services.feed import *
from sqlalchemy.orm import Session
from services.telegram import send_movie_download_message_by_work_id, DownloadStatus


router = APIRouter()


@router.get(
    "/get_downloading_torrents",
)
async def get(isValid: str = Depends(tokenInterceptor)):

    qb_client = QB()

    return qb_client.get_downloading_torrents()


@router.post("/delete_torrent")
async def delete(
    torrent_hash: str = Body(...),
    delete_files: bool = Body(True),
    isValid: str = Depends(tokenInterceptor),
):
    qb_client = QB()

    try:
        qb_client.delete_torrent(torrent_hash, delete_files=delete_files)
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
            await movie_subscribe_service(
                db, MovieFeedOperation.MARK_DOWNLOADED, work_id
            )
            await send_movie_download_message_by_work_id(
                work_id, DownloadStatus.START_DOWNLOAD
            )

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=400, detail="Failed to add torrent")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add_torrent_file")
async def add_torrent_file(
    file: UploadFile = File(...),
    save_path: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    try:
        torrent_data = BytesIO(await file.read())
        qb_client = QB()

        success = qb_client.add_torrent_file(file.filename, torrent_data, save_path)

        if success:
            return {"message": "Torrent added successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to add torrent")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
