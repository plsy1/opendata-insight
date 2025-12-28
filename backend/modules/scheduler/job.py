import asyncio
from database import get_db
from modules.metadata.prowlarr import Prowlarr
from config import _config
from modules.metadata.avbase import *
from database import get_db, EmbyMovie
from modules.mediaServer.emby import emby_get_all_movies
from utils.logs import LOG_ERROR, LOG_INFO
from datetime import datetime, timedelta
from services.feed import *
from services.telegram import send_movie_download_message_by_work_id, DownloadStatus
from pathlib import Path


async def refresh_movies_feeds():
    try:
        PROWLARR_URL = _config.get("PROWLARR_URL")
        PROWLARR_KEY = _config.get("PROWLARR_KEY")

        prowlarr = Prowlarr(PROWLARR_URL, PROWLARR_KEY)

        from modules.downloader.qbittorrent import _qb_instance

        save_path = Path(_config.get("DOWNLOAD_PATH", ""))

        db = next(get_db())
        feeds = movie_subscribe_list_service(db, MovieStatus.SUBSCRIBE, True)

        if not feeds:
            return

        for feed in feeds:
            work_id = feed.work_id
            search_data = prowlarr.search(query=work_id, page=1, page_size=5)

            if not search_data:
                continue

            search_data.sort(key=lambda x: x.get("seeders", 0), reverse=True)
            best_seed = search_data[0]

            download_link = best_seed.get("downloadUrl")

            if not download_link:
                continue

            success = await _qb_instance.add_torrent_url(download_link, save_path)

            if success:
                await movie_subscribe_service(
                    db, MovieFeedOperation.MARK_DOWNLOADED, work_id
                )

                await send_movie_download_message_by_work_id(
                    work_id, DownloadStatus.START_DOWNLOAD
                )

            await asyncio.sleep(5)
        return

    except Exception as e:
        LOG_ERROR(e)
        return


async def refresh_actress_feeds():
    try:
        db = next(get_db())
        feeds = actor_list_service(db, ActorListType.SUBSCRIBE)

        if not feeds:
            return

        for feed in feeds:
            name = feed.name

            items = await get_movie_info_by_actress_name(
                name, 1, changeImagePrefix=False
            )

            valid_items = []
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

            work_id = item.id

            await movie_subscribe_service(db, MovieFeedOperation.ADD, work_id)

            await send_movie_download_message_by_work_id(
                work_id, DownloadStatus.ADD_SUBSCRIBE
            )

            await asyncio.sleep(5)

    except Exception as e:
        LOG_ERROR(e)


async def refresh_feeds():
    await refresh_actress_feeds()
    await refresh_movies_feeds()


def update_emby_movies_in_db():
    db = next(get_db())
    try:
        movies: List[dict] = emby_get_all_movies()
        print("hello")
        db.query(EmbyMovie).delete()
        db.commit()

        for m in movies:
            new_movie = EmbyMovie(
                name=m.get("name"),
                primary=m.get("primary"),
                serverId=m.get("serverId"),
                indexLink=m.get("indexLink"),
                ProductionYear=m.get("ProductionYear"),
            )
            db.add(new_movie)

        db.commit()

    except Exception as e:
        db.rollback()
        LOG_ERROR(f"Error updating Emby movies: {e}")
    finally:
        db.close()


async def update_avbase_release_everyday():
    """
    抓取当天作品列表，并写入数据库
    """

    from modules.metadata.avbase import get_release_by_date

    try:
        date_str = datetime.today().strftime("%Y-%m-%d")
        await get_release_by_date(date_str)
    except Exception as e:
        LOG_ERROR(e)


def clean_cache_dir(max_image_cache_hours=1):
    from pathlib import Path

    CACHE_DIR = _config.get("CACHE_DIR")
    now = datetime.now()
    for f in Path(CACHE_DIR).glob("*"):
        if now - datetime.fromtimestamp(f.stat().st_mtime) > timedelta(
            hours=max_image_cache_hours
        ):
            f.unlink()


async def update_fc2_ranking_in_db():
    from database import FC2Ranking
    from modules.metadata.fc2 import RankingType, get_ranking

    db = next(get_db())

    try:
        for term in RankingType:
            for page in range(1, 6):
                LOG_INFO(f"[FC2] Updating term={term.value} page={page}")

                items = await get_ranking(page=page, term=term)
                if not items:
                    LOG_ERROR(f"[FC2] No items found for term={term.value} page={page}")
                    continue

                current_ids = {item.article_id for item in items}

                existing_records = (
                    db.query(FC2Ranking)
                    .filter(
                        FC2Ranking.term == term.value,
                        FC2Ranking.page == page,
                    )
                    .all()
                )

                existing_map = {r.article_id: r for r in existing_records}

                for record in existing_records:
                    if record.article_id not in current_ids:
                        db.delete(record)

                for item in items:
                    old = existing_map.get(item.article_id)

                    if old is None:
                        db.add(
                            FC2Ranking(
                                term=term.value,
                                article_id=item.article_id,
                                page=page,
                                rank=item.rank,
                                title=item.title,
                                url=str(item.url),
                                cover=str(item.cover) if item.cover else None,
                                owner=item.owner,
                                rating=item.rating,
                                comment_count=item.comment_count,
                                hot_comments=item.hot_comments,
                                crawled_at=datetime.now(),
                            )
                        )
                    else:
                        changed = False

                        def set_if_changed(field, new_value):
                            nonlocal changed
                            if getattr(old, field) != new_value:
                                setattr(old, field, new_value)
                                changed = True

                        set_if_changed("rank", item.rank)
                        set_if_changed("title", item.title)
                        set_if_changed("rating", item.rating)
                        set_if_changed("comment_count", item.comment_count)
                        set_if_changed("hot_comments", item.hot_comments)

                        if changed:
                            old.crawled_at = datetime.now()

                db.commit()
                await asyncio.sleep(2)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        LOG_INFO("[FC2] FC2 ranking update task completed")
