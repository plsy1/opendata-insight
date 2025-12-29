from modules.metadata.avbase import *
from database import get_db, EmbyMovie
from utils.logs import LOG_ERROR
from services.emby import get_all_movies_service


async def update_emby_movies_in_db():
    db = next(get_db())
    try:
        movies: List[dict] = await get_all_movies_service()
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
