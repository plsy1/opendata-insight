import asyncio
from modules.metadata.avbase import parse_actor_information
from utils.logs import LOG_ERROR, LOG_INFO
from database import get_db
from database.models.actors import ActorData

async def update_actor_data_periodic():
    try:
        db = next(get_db())
        # 取出缺少 ruby 字段的演员进行更新
        actors = db.query(ActorData).filter(ActorData.ruby == None).all()
        
        if not actors:
            # 只有没有需要更新的数据时才不输出日志，保持安静
            return
            
        LOG_INFO(f"[ACTORS] Periodic updating {len(actors)} actors with missing data...")
        for actor in actors:
            try:
                url = f"https://www.avbase.net/talents/{actor.name}"
                data = await parse_actor_information(url)
                if data and data.ruby:
                    actor.ruby = data.ruby
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
