import uuid, asyncio
from core.database import get_db, RSSItem, RSSFeed, AvbaseReleaseEveryday
from modules.metadata.prowlarr import Prowlarr
from modules.downloader.qbittorrent import QB
from core.config import _config
from modules.notification.telegram import _telegram_bot
from modules.notification.telegram.text import *
from modules.metadata.avbase import *
from core.database import get_db, EmbyMovie
from modules.mediaServer.emby import emby_get_all_movies
from core.logs import LOG_ERROR
from datetime import datetime, timedelta


async def refresh_movies_feeds():
    try:
        from urllib.parse import urlparse

        QB_URL = _config.get("QB_URL")
        parsed = urlparse(QB_URL)
        QB_HOST = parsed.hostname
        if parsed.port is not None:
            QB_PORT = parsed.port
        else:
            if parsed.scheme == "http":
                QB_PORT = 80
            elif parsed.scheme == "https":
                QB_PORT = 443

        QB_USERNAME = _config.get("QB_USERNAME")
        QB_PASSWORD = _config.get("QB_PASSWORD")

        qb_client = QB(
            host=QB_HOST,
            port=QB_PORT,
            username=QB_USERNAME,
            password=QB_PASSWORD,
        )

        PROWLARR_URL = _config.get("PROWLARR_URL")
        PROWLARR_KEY = _config.get("PROWLARR_KEY")

        prowlarr = Prowlarr(PROWLARR_URL, PROWLARR_KEY)

        db = next(get_db())
        feeds = db.query(RSSItem).filter(RSSItem.downloaded == False).all()

        if not feeds:
            return

        for feed in feeds:
            keyword = feed.keyword
            movie_link = feed.link

            search_data = prowlarr.search(query=keyword, page=1, page_size=5)

            if not search_data:
                continue

            search_data.sort(key=lambda x: x.get("seeders", 0), reverse=True)
            best_seed = search_data[0]

            download_link = best_seed.get("downloadUrl")

            if not download_link:
                continue

            random_tag = str(uuid.uuid4())[:8]

            tags = f"Ecchi,{random_tag}"

            DOWNLOAD_PATH = _config.get("DOWNLOAD_PATH")

            success = qb_client.add_torrent_url(
                download_link, f"{DOWNLOAD_PATH}/{feed.actors}", tags
            )

            if success:

                QB_KEYWORD_FILTER = [
                    kw.strip()
                    for kw in _config.get("QB_KEYWORD_FILTER", "").split(",")
                    if kw.strip()
                ]

                qb_client.filter_after_add_by_tag(random_tag, QB_KEYWORD_FILTER)
                keyword_feed = (
                    db.query(RSSItem).filter(RSSItem.keyword == keyword).first()
                )
                if keyword_feed:
                    keyword_feed.downloaded = True
                    db.commit()

                movie_info = await get_actors_from_work(
                    movie_link, changeImagePrefix=False
                )
                movie_details = DownloadInformation(keyword, movie_info)

                await _telegram_bot.send_message_with_image(
                    str(movie_info.props.pageProps.work.products[0].image_url),
                    movie_details,
                )

            await asyncio.sleep(5)
        return

    except Exception as e:
        LOG_ERROR(e)
        return


async def refresh_actress_feeds():
    try:
        db = next(get_db())

        feeds = db.query(RSSFeed).all()
        if not feeds:
            return

        for feed in feeds:
            isExist = False
            name = feed.title
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
            existing_feed = db.query(RSSItem).filter_by(keyword=item.id).first()
            if existing_feed:
                isExist = True
                existing_feed.img = str(item.img_url)
                existing_feed.link = str(item.full_id)
                db.add(existing_feed)
                rss_item = existing_feed
            else:
                rss_item = RSSItem(
                    actors=",".join(item.actors),
                    keyword=item.id,
                    img=str(item.img_url),
                    link=str(item.full_id),
                    downloaded=False,
                )
                db.add(rss_item)

            try:
                db.commit()
                db.refresh(rss_item)
                if not isExist:
                    movie_info = await get_actors_from_work(
                        rss_item.link, changeImagePrefix=False
                    )
                    movie_details = movieInformation(rss_item.keyword, movie_info)

                    await _telegram_bot.send_message_with_image(
                        rss_item.img, movie_details
                    )

            except Exception as e:
                db.rollback()
                LOG_ERROR(e)

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
    异步抓取当天作品列表，并写入数据库
    数据库操作同步执行（db = next(get_db())）
    """
    date_str = datetime.today().strftime("%Y-%m-%d")

    record_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    db = next(get_db())

    try:
        result = await get_release_grouped_by_prefix(date_str)
        json_data = json.dumps(
            [r.model_dump() for r in result], ensure_ascii=False, default=str
        )
        db.query(AvbaseReleaseEveryday).filter(
            AvbaseReleaseEveryday.date == record_date
        ).delete()
        db.commit()

        record = AvbaseReleaseEveryday(date=record_date, data_json=json_data)
        db.add(record)
        db.commit()

    except Exception as e:
        db.rollback()
    finally:
        db.close()


def clean_cache_dir(max_age_hours=48):
    from pathlib import Path

    CACHE_DIR = _config.get("CACHE_DIR")
    now = datetime.now()
    for f in Path(CACHE_DIR).glob("*"):
        if now - datetime.fromtimestamp(f.stat().st_mtime) > timedelta(
            hours=max_age_hours
        ):
            f.unlink()
