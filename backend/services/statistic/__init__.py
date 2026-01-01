from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from database import MovieSubscribe, MovieData


def stat_overview(db: Session) -> dict:
    total = db.query(func.count(MovieSubscribe.movie_id)).scalar()

    downloaded = (
        db.query(func.count(MovieSubscribe.movie_id))
        .filter(MovieSubscribe.is_downloaded == True)
        .scalar()
    )

    return {
        "total": total,
        "downloaded": downloaded,
        "not_downloaded": total - downloaded,
    }


def stat_daily_subscribe(db: Session) -> list[dict]:
    rows = (
        db.query(
            func.date(MovieSubscribe.created_at).label("day"),
            func.count(MovieSubscribe.movie_id).label("count"),
        )
        .group_by(func.date(MovieSubscribe.created_at))
        .order_by(func.date(MovieSubscribe.created_at))
        .all()
    )

    return [{"date": day, "count": count} for day, count in rows]


def stat_workid_prefix(db: Session, limit: int = 10) -> list[dict]:
    prefix = func.substr(MovieData.work_id, 1, func.instr(MovieData.work_id, "-") - 1)

    rows = (
        db.query(prefix.label("prefix"), func.count(MovieData.id).label("count"))
        .join(MovieSubscribe, MovieData.id == MovieSubscribe.movie_id)
        .filter(MovieData.work_id.contains("-"))
        .group_by(prefix)
        .order_by(func.count(MovieData.id).desc())
        .limit(limit)
        .all()
    )

    return [{"studio": prefix, "count": count} for prefix, count in rows]


def stat_actors_subscribed(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(MovieData.actors, MovieData.casts)
        .join(MovieSubscribe, MovieData.id == MovieSubscribe.movie_id)
        .filter((MovieData.actors.isnot(None)) | (MovieData.casts.isnot(None)))
        .all()
    )

    counter = Counter()

    for actors_list, casts_list in rows:
        movie_actor_names = set()

        for actor in actors_list or []:
            name = actor.get("name")
            if isinstance(name, str):
                name = name.strip()
                if name:
                    movie_actor_names.add(name)

        for cast in casts_list or []:
            name = cast.get("name")
            if isinstance(name, str):
                name = name.strip()
                if name:
                    movie_actor_names.add(name)
        for name in movie_actor_names:
            counter[name] += 1

    return [
        {"actor": actor, "count": count} for actor, count in counter.most_common(limit)
    ]
