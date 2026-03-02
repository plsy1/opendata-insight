import asyncio
from modules.metadata.avbase import parse_actor_information
from utils.logs import LOG_ERROR, LOG_INFO
from database import get_db
from database.models.actors import ActorData

async def update_actor_data_periodic():
    try:
        db = next(get_db())
        # 取出缺少 avatar_url 字段（NULL 或 空字符串）的演员进行更新
        actors = db.query(ActorData).filter(
            (ActorData.avatar_url == None) | (ActorData.avatar_url == "")
        ).all()
        
        if not actors:
            # 只有没有需要更新的数据时才不输出日志，保持安静
            return
            
        LOG_INFO(f"[ACTORS] Periodic updating {len(actors)} actors with missing data...")
        for actor in actors:
            try:
                url = f"https://www.avbase.net/talents/{actor.name}"
                data = await parse_actor_information(url)
                if data:
                    # 获取解析到的所有字段字典（排除 name 避免意外覆盖主记录名）
                    update_data = data.model_dump(exclude={"name"}, exclude_unset=True)
                    for key, value in update_data.items():
                        if value is not None:
                            setattr(actor, key, value)
                db.commit()
                # 睡两秒，防止请求太快被封
                await asyncio.sleep(2)
            except Exception as e:
                db.rollback()
                LOG_ERROR(f"[ACTORS] Failed to update {actor.name}: {e}")
                
    except Exception as e:
        LOG_ERROR(f"[ACTORS] Periodic Actor data task error: {e}")
    finally:
        db.close()
        LOG_INFO("[ACTORS] Periodic Actor data update task completed")
