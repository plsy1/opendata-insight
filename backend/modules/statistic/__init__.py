from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from database import RSSItem


def stat_overview(db: Session) -> dict:
    total = db.query(func.count(RSSItem.id)).scalar()

    downloaded = (
        db.query(func.count(RSSItem.id)).filter(RSSItem.downloaded == True).scalar()
    )

    return {
        "total": total,
        "downloaded": downloaded,
        "not_downloaded": total - downloaded,
    }


def stat_daily(db: Session) -> list[dict]:
    rows = (
        db.query(
            func.date(RSSItem.created_at).label("day"),
            func.count(RSSItem.id).label("count"),
        )
        .group_by(func.date(RSSItem.created_at))
        .order_by(func.date(RSSItem.created_at))
        .all()
    )

    return [{"date": day, "count": count} for day, count in rows]


def stat_studio(db: Session, limit: int = 10) -> list[dict]:
    studio = func.substr(RSSItem.keyword, 1, func.instr(RSSItem.keyword, "-") - 1)

    rows = (
        db.query(studio.label("studio"), func.count(RSSItem.id).label("count"))
        .filter(RSSItem.keyword.contains("-"))
        .group_by(studio)
        .order_by(func.count(RSSItem.id).desc())
        .limit(limit)
        .all()
    )

    return [{"studio": studio, "count": count} for studio, count in rows]


def stat_actors(db: Session, limit: int = 10) -> list[dict]:
    rows = db.query(RSSItem.actors).filter(RSSItem.actors.isnot(None)).all()

    counter = Counter()

    for (actors_str,) in rows:
        if not actors_str:
            continue

        # 常见分隔符统一处理
        actors = (
            actors_str.replace("、", ",").replace("/", ",").replace("|", ",").split(",")
        )

        for actor in actors:
            actor = actor.strip()
            if actor:
                counter[actor] += 1

    return [
        {"actor": actor, "count": count} for actor, count in counter.most_common(limit)
    ]
