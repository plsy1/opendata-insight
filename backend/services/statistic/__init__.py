from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from database import MovieSubscribe, MovieData, MovieProduct


def _rank_unique_names_by_movie(
    movie_values: list[tuple[int, list[str]]],
    limit: int,
) -> list[dict]:
    counts: Counter[str] = Counter()
    display_names: dict[str, str] = {}

    for _movie_id, values in movie_values:
        movie_names: set[str] = set()
        for value in values:
            name = str(value or "").strip()
            if not name:
                continue
            key = name.casefold()
            display_names.setdefault(key, name)
            movie_names.add(key)
        counts.update(movie_names)

    return [
        {"name": display_names[key], "count": count}
        for key, count in counts.most_common(limit)
    ]


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


def stat_product_metadata(db: Session, limit: int = 10) -> dict[str, list[dict]]:
    rows = (
        db.query(
            MovieData.id,
            MovieProduct.maker,
            MovieProduct.label,
            MovieProduct.series,
        )
        .join(MovieSubscribe, MovieData.id == MovieSubscribe.movie_id)
        .join(MovieProduct, MovieProduct.work_id == MovieData.id)
        .all()
    )

    grouped: dict[str, dict[int, list[str]]] = {
        "makers": {},
        "labels": {},
        "series": {},
    }
    for movie_id, maker, label, series in rows:
        for key, value in (
            ("makers", maker),
            ("labels", label),
            ("series", series),
        ):
            grouped[key].setdefault(movie_id, []).append(value)

    return {
        key: _rank_unique_names_by_movie(list(values.items()), limit)
        for key, values in grouped.items()
    }


def stat_makers(db: Session, limit: int = 10) -> list[dict]:
    return stat_product_metadata(db, limit)["makers"]


def stat_labels(db: Session, limit: int = 10) -> list[dict]:
    return stat_product_metadata(db, limit)["labels"]


def stat_series(db: Session, limit: int = 10) -> list[dict]:
    return stat_product_metadata(db, limit)["series"]


def stat_taxonomy_metadata(db: Session, limit: int = 10) -> dict[str, list[dict]]:
    rows = (
        db.query(MovieData.id, MovieData.genres, MovieData.tags)
        .join(MovieSubscribe, MovieData.id == MovieSubscribe.movie_id)
        .all()
    )
    genre_values = []
    tag_values = []
    taxonomy_values = []
    for movie_id, genres, tags in rows:
        genre_names = [str(genre) for genre in (genres or [])]
        tag_names = []
        for tag in tags or []:
            if isinstance(tag, dict):
                tag_names.append(tag.get("name") or "")
            else:
                tag_names.append(str(tag))

        genre_values.append((movie_id, genre_names))
        tag_values.append((movie_id, tag_names))
        taxonomy_values.append((movie_id, [*genre_names, *tag_names]))

    return {
        "taxonomy": _rank_unique_names_by_movie(taxonomy_values, limit),
        "genres": _rank_unique_names_by_movie(genre_values, limit),
        "tags": _rank_unique_names_by_movie(tag_values, limit),
    }


def stat_taxonomy(db: Session, limit: int = 10) -> list[dict]:
    return stat_taxonomy_metadata(db, limit)["taxonomy"]


def stat_genres(db: Session, limit: int = 10) -> list[dict]:
    return stat_taxonomy_metadata(db, limit)["genres"]


def stat_tags(db: Session, limit: int = 10) -> list[dict]:
    return stat_taxonomy_metadata(db, limit)["tags"]
