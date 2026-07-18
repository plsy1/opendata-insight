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
from services.subscribe import *
from services.telegram import *
from services.downloader import (
    build_download_tags,
    enrich_downloading_torrents,
    resolve_download_media_type,
)
from services.system import replace_domain_in_value
from schemas.downloader import DeleteTorrentOut, DownloadingTorrentOut


router = APIRouter()


@router.get(
    "/get_downloading_torrents",
    response_model=list[DownloadingTorrentOut],
)
async def get(db: Session = Depends(get_db)):

    from modules.downloader.qbittorrent import _qb_instance

    torrents = await _qb_instance.get_downloading_torrents()
    result = enrich_downloading_torrents(db, torrents)
    return replace_domain_in_value(result)


@router.post("/delete_torrent", response_model=DeleteTorrentOut)
async def delete(
    torrent_hash: str = Body(...),
    delete_files: bool = Body(True),
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
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/add_torrent_url",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def add_torrent_url(
    work_id: str,
    download_link: str,
    save_path: str,
    media_type: str = "",
    db: Session = Depends(get_db),
):
    try:
        resolved_media_type = resolve_download_media_type(media_type, work_id)
        if media_type and resolved_media_type != media_type.strip().casefold():
            raise HTTPException(status_code=422, detail="Unsupported media type")

        save_path = Path(
            save_path or _config.get_download_path(resolved_media_type)
        )

        if work_id and resolved_media_type != "fc2":
            records = db.query(MovieData).filter(MovieData.work_id == work_id).first()

            if records:
                movie_out = MovieDataOut.model_validate(records)

                names = []
                seen = set()

                for person in (movie_out.actors or []) + (movie_out.casts or []):
                    name = person.get("name")
                    if isinstance(name, str):
                        name = name.strip()
                        if name and name not in seen:
                            seen.add(name)
                            names.append(name)

                top_names = ", ".join(names[:3])

                save_path = save_path / top_names

        from modules.downloader.qbittorrent import _qb_instance

        download_tags = build_download_tags(
            _qb_instance.tags,
            work_id,
            resolved_media_type,
        )

        if download_link.startswith("magnet:"):
            success = await _qb_instance.add_torrent_url(
                download_link, str(save_path), tags=download_tags
            )
        else:
            torrent_data = await _qb_instance.download_torrent_file(download_link)
            if torrent_data:
                torrent_name = work_id if work_id else "direct_add_torrent"
                if isinstance(torrent_data, str) and torrent_data.startswith("magnet:"):
                    success = await _qb_instance.add_torrent_url(
                        torrent_data, str(save_path), tags=download_tags
                    )
                else:
                    success = await _qb_instance.add_torrent_file(
                        torrent_name, torrent_data, str(save_path), tags=download_tags
                    )
            else:
                success = False

        if success and work_id and resolved_media_type != "fc2":
            movie_subscribe_service(db, MovieFeedOperation.MARK_DOWNLOADED, work_id)
            await send_movie_download_message_by_work_id(
                db, work_id, DownloadStatus.START_DOWNLOAD
            )

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        elif success:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(status_code=400, detail="Failed to add torrent")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
