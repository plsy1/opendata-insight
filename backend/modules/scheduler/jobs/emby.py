from modules.metadata.avbase import *
from database import get_db, EmbyMovie
from modules.mediaServer.emby import emby_get_all_movies
from utils.logs import LOG_ERROR


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
