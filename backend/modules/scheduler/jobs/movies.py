import asyncio
from modules.metadata.avbase import *
from modules.metadata.fc2 import *
from utils.logs import LOG_ERROR, LOG_INFO
from datetime import datetime
from database import get_db, FC2Ranking
from database import avbaseNewbie, avbasePopular


async def update_avbase_release_everyday():
    try:
        db = next(get_db())
        date_str = datetime.today().strftime("%Y-%m-%d")
        await fetch_avbase_release_by_date_and_write_db(db, date_str)
    except Exception as e:
        LOG_ERROR(e)
    finally:
        db.close()
        LOG_INFO("[AVBASE] Update avbase release everyday task completed")


async def update_fc2_ranking():
    try:
        db = next(get_db())
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


async def update_avbase_index_actor_service():
    try:
        db = next(get_db())
        newbie_data_list, popular_data_list = await parse_actor_lists()

        db.query(avbaseNewbie).delete()
        db.query(avbasePopular).delete()
        db.flush()

        newbie_records = [
            avbaseNewbie(
                name=a.name,
                avatar_url=a.avatar_url,
            )
            for a in newbie_data_list
        ]

        popular_records = [
            avbasePopular(
                name=a.name,
                avatar_url=a.avatar_url,
            )
            for a in popular_data_list
        ]

        db.add_all(newbie_records + popular_records)
        db.commit()

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        LOG_INFO("[AVBASE] Update avbase index actor task completed")
