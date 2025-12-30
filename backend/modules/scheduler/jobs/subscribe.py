import asyncio
from database import get_db
from config import _config
from utils.logs import LOG_ERROR
from datetime import datetime
from services.subscribe import *
from services.telegram import *
from services.avbase import *
from pathlib import Path


def _get_actor_name_from_db(db: Session, work_id: str):

    records = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    movie_out = MovieDataOut.model_validate(records)

    top_names_list = [cast["name"] for cast in movie_out.casts if cast.get("name")][:3]

    top_names = ", ".join(top_names_list)

    return top_names


async def _refresh_movie_feeds():
    try:

        from modules.indexer.prowlarr import _prowlarr_instance
        from modules.downloader.qbittorrent import _qb_instance

        save_path = Path(_config.get("DOWNLOAD_PATH", ""))

        db = next(get_db())
        feeds = movie_subscribe_list_service(db, MovieStatus.SUBSCRIBE)

        if not feeds:
            return

        for feed in feeds:
            work_id = feed.work_id
            search_data = await _prowlarr_instance.search(
                query=work_id, page=1, page_size=5
            )

            if not search_data:
                continue

            search_data.sort(key=lambda x: x.get("seeders", 0), reverse=True)
            best_seed = search_data[0]

            download_link = best_seed.get("downloadUrl")

            if not download_link:
                continue

            names = _get_actor_name_from_db(work_id)

            path = save_path / names

            success = await _qb_instance.add_torrent_url(download_link, path)

            if success:
                movie_subscribe_service(db, MovieFeedOperation.MARK_DOWNLOADED, work_id)
                await send_movie_download_message_by_work_id(
                    db, work_id, DownloadStatus.START_DOWNLOAD
                )
            await asyncio.sleep(5)
        return

    except Exception as e:
        LOG_ERROR(e)
        return
    finally:
        db.close()


async def _refresh_actor_feeds():
    try:
        db = next(get_db())
        feeds = actor_list_service(db, ActorListType.SUBSCRIBE)

        if not feeds:
            return

        for feed in feeds:
            name = feed.name

            items = await get_movie_list_by_actor_name_service(name, 1)

            valid_items: list[MoviePoster] = []
            for item in items:
                try:
                    release_date = datetime.strptime(item.release_date, "%Y/%m/%d")
                except ValueError:
                    continue

                if release_date > datetime.today() and len(item.actors) <= 2:
                    valid_items.append(item)

            if not valid_items:
                continue

            item = valid_items[-1]

            await get_information_by_work_id_service(db, item.full_id)

            movie_subscribe_service(db, MovieFeedOperation.ADD, item.id)

            await send_movie_download_message_by_work_id(
                db, item.id, DownloadStatus.ADD_SUBSCRIBE
            )

            await asyncio.sleep(5)

    except Exception as e:
        LOG_ERROR(e)
    finally:
        db.close()


async def refresh_feeds():
    await _refresh_actor_feeds()
    await _refresh_movie_feeds()
