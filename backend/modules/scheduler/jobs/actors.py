import asyncio
from datetime import datetime, timedelta
from sqlalchemy import or_

from config import _config
from utils.logs import LOG_ERROR, LOG_INFO
from database import get_db
from database.models.actors import ActorData
from services.avbase import fetch_actor_information_from_source


async def update_actor_data_periodic():
    db = None
    try:
        db = next(get_db())
        try:
            cache_hours = float(_config.get("AVBASE_ACTOR_CACHE_HOURS", 24))
        except (TypeError, ValueError):
            cache_hours = 24
        refresh_before = datetime.now() - timedelta(hours=max(0, cache_hours))

        # 取出缺少 avatar_url 字段（NULL 或 空字符串）的演员进行更新
        actors = (
            db.query(ActorData)
            .filter(
                or_(ActorData.avatar_url.is_(None), ActorData.avatar_url == ""),
                or_(
                    ActorData.updated_at.is_(None),
                    ActorData.updated_at <= refresh_before,
                ),
            )
            .all()
        )

        if not actors:
            # 只有没有需要更新的数据时才不输出日志，保持安静
            return

        LOG_INFO(f"[ACTORS] Periodic updating {len(actors)} actors with missing data...")
        for actor in actors:
            try:
                data = await fetch_actor_information_from_source(actor.name)
                if data:
                    # 获取解析到的所有字段字典（排除 name 避免意外覆盖主记录名）
                    update_data = data.model_dump(exclude={"name"}, exclude_unset=True)
                    for key, value in update_data.items():
                        if value is not None:
                            setattr(actor, key, value)
                actor.updated_at = datetime.now()
                db.commit()
                # 睡两秒，防止请求太快被封
                await asyncio.sleep(2)
            except Exception as e:
                db.rollback()
                LOG_ERROR(f"[ACTORS] Failed to update {actor.name}: {e}")

    except Exception as e:
        LOG_ERROR(f"[ACTORS] Periodic Actor data task error: {e}")
    finally:
        if db is not None:
            db.close()
        LOG_INFO("[ACTORS] Periodic Actor data update task completed")
