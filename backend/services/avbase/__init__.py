import asyncio
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote, urlencode

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, selectinload

from config import _config
from database import (
    ActorData,
    AvbaseReleaseCache,
    MovieData,
    MovieProduct,
    MovieSubscribe,
    avbaseNewbie,
    avbasePopular,
)
from modules.metadata.avbase import (
    avbase_client,
    parse_actor_information,
    parse_actor_lists,
    parse_min_date,
    parse_movie_information,
    parse_movie_list,
    parse_release_works,
)
from schemas.actor import ActorDataOut, AvbaseIndexActorOut
from schemas.avbase import MoviePoster
from schemas.movies import MovieDataOut, MovieProductOut
from utils.logs import LOG_ERROR


AVBASE_BASE_URL = "https://www.avbase.net"
AVBASE_RELEASE_SOURCE = "avbase_release"
AVBASE_DETAIL_SOURCE = "avbase_detail"
DEFAULT_RELEASE_RETENTION_DAYS = 30
DOWNLOADED_METADATA_MAX_AGE = timedelta(days=3)
ACTIVE_SUBSCRIPTION_METADATA_MAX_AGE = timedelta(days=1)
_MOVIE_REFRESH_LOCKS: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
ACTOR_SOURCE_METADATA_FIELDS = frozenset(
    {
        "avatar_url",
        "birthday",
        "blood_type",
        "bust",
        "cup",
        "height",
        "hip",
        "hobby",
        "aliases",
        "prefectures",
        "ruby",
        "social_media",
        "waist",
    }
)


def _cache_hours() -> float:
    try:
        return float(_config.get("AVBASE_ACTOR_CACHE_HOURS", 24))
    except (TypeError, ValueError):
        return 24.0


def _release_retention_days() -> int:
    try:
        return int(
            _config.get(
                "AVBASE_RELEASE_RETENTION_DAYS",
                DEFAULT_RELEASE_RETENTION_DAYS,
            )
        )
    except (TypeError, ValueError):
        return DEFAULT_RELEASE_RETENTION_DAYS


def _actor_cache_expired(
    record: Optional[ActorData],
    *,
    now: Optional[datetime] = None,
    cache_hours: Optional[float] = None,
) -> bool:
    if record is None or record.avatar_url == "None" or record.updated_at is None:
        return True

    ttl = _cache_hours() if cache_hours is None else cache_hours
    if ttl <= 0:
        return True

    current_time = now or datetime.now()
    return current_time - record.updated_at >= timedelta(hours=ttl)


async def fetch_actor_information_from_source(name: str) -> ActorDataOut:
    url = f"{AVBASE_BASE_URL}/talents/{quote(name, safe='')}"
    content = await avbase_client.fetch_html(url)
    return parse_actor_information(content)


async def fetch_actor_lists_from_source() -> tuple[
    list[AvbaseIndexActorOut], list[AvbaseIndexActorOut]
]:
    content = await avbase_client.fetch_html(AVBASE_BASE_URL)
    return parse_actor_lists(content)


def apply_actor_source_metadata(record: ActorData, data: ActorDataOut) -> None:
    """Apply only mutable source metadata to an existing actor record."""
    update_data = data.model_dump(
        include=ACTOR_SOURCE_METADATA_FIELDS,
        exclude_unset=True,
    )
    for key, value in update_data.items():
        if value is not None:
            setattr(record, key, value)


async def get_movie_list_by_actor_name_service(
    name: str, page: int
) -> list[MoviePoster]:
    path_name = quote(name, safe="")
    query = urlencode({"q": "", "page": page})
    content = await avbase_client.fetch_html(
        f"{AVBASE_BASE_URL}/talents/{path_name}?{query}"
    )
    return parse_movie_list(content)


async def get_movie_list_by_keywords_service(
    keywords: str, page: int
) -> list[MoviePoster]:
    query = urlencode({"q": keywords, "page": page})
    content = await avbase_client.fetch_html(f"{AVBASE_BASE_URL}/works?{query}")
    return parse_movie_list(content)


async def get_actor_information_by_name_service(
    db: Session, name: str
) -> ActorDataOut:
    record = db.query(ActorData).where(ActorData.name == name).first()
    cache_expired = _actor_cache_expired(record)

    if record and record.avatar_url == "None":
        record.avatar_url = None

    if cache_expired:
        try:
            data = await fetch_actor_information_from_source(name)
        except HTTPException as exc:
            if record is not None:
                LOG_ERROR(f"[AVBASE] Serving stale actor cache for {name}: {exc.detail}")
                return ActorDataOut.model_validate(record)
            raise

        if record is None:
            actor_fields = data.model_dump(
                include=ACTOR_SOURCE_METADATA_FIELDS | {"name"},
                exclude_unset=True,
                exclude_none=True,
            )
            actor_fields["name"] = actor_fields.get("name") or name
            record = ActorData(**actor_fields)
            db.add(record)
        else:
            apply_actor_source_metadata(record, data)

        record.updated_at = datetime.now()
        db.commit()
        db.refresh(record)

    return ActorDataOut.model_validate(record)


async def get_avbase_index_actor_service(db: Session):
    newbie_records = db.query(avbaseNewbie).all()
    popular_records = db.query(avbasePopular).all()

    if not newbie_records or not popular_records:
        newbie_data_list, popular_data_list = await fetch_actor_lists_from_source()

        newbie_records = [
            avbaseNewbie(name=item.name, avatar_url=item.avatar_url)
            for item in newbie_data_list
        ]
        popular_records = [
            avbasePopular(name=item.name, avatar_url=item.avatar_url)
            for item in popular_data_list
        ]

        db.add_all(newbie_records)
        db.add_all(popular_records)
        db.commit()

        for record in newbie_records + popular_records:
            db.refresh(record)

    return {
        "newbie_talents": [
            AvbaseIndexActorOut.model_validate(record) for record in newbie_records
        ],
        "popular_talents": [
            AvbaseIndexActorOut.model_validate(record) for record in popular_records
        ],
    }


async def get_information_by_work_id_service(
    db: Session, full_id: str
) -> MovieDataOut:
    work_id = full_id.split(":", 1)[1] if ":" in full_id else full_id
    movie = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    if movie is None:
        return await refresh_information_by_work_id_service(db, full_id)

    if movie.source_type != AVBASE_DETAIL_SOURCE:
        movie.source_type = AVBASE_DETAIL_SOURCE
        movie.last_seen_at = datetime.now()
        db.commit()
        db.refresh(movie)

    return _movie_data_out(movie)


def _movie_data_out(movie: MovieData) -> MovieDataOut:
    movie_out = MovieDataOut.model_validate(movie)
    merged_product = _merge_products(movie_out.products)
    if merged_product is None:
        raise HTTPException(status_code=502, detail="作品缺少产品信息")

    if not merged_product.image_url and merged_product.thumbnail_url:
        merged_product.image_url = merged_product.thumbnail_url.replace(
            "ps.jpg", "pl.jpg"
        )

    movie_out.primary_product = merged_product
    return movie_out


def _metadata_is_fresh(
    movie: MovieData,
    max_age: timedelta,
    *,
    now: Optional[datetime] = None,
) -> bool:
    if movie.metadata_updated_at is None:
        return False
    return (now or datetime.now()) - movie.metadata_updated_at < max_age


async def _fetch_and_store_movie_information(
    db: Session,
    full_id: str,
    movie: Optional[MovieData],
) -> MovieDataOut:
    encoded_id = quote(full_id, safe=":")
    content = await avbase_client.fetch_html(
        f"{AVBASE_BASE_URL}/works/{encoded_id}"
    )
    work = parse_movie_information(content)
    movie_out = _gen_movie_data(work)
    product_outs = _gen_movie_product(work.get("products", []))
    if not product_outs:
        raise HTTPException(status_code=502, detail="作品缺少产品信息")

    if movie is None:
        movie = MovieData(work_id=movie_out.work_id)
        db.add(movie)

    for field in (
        "work_id",
        "prefix",
        "title",
        "min_date",
        "casts",
        "actors",
        "tags",
        "genres",
    ):
        setattr(movie, field, getattr(movie_out, field))

    existing_products = {
        product.product_id: product for product in list(movie.products)
    }
    incoming_product_ids = set()
    for product_out in product_outs:
        incoming_product_ids.add(product_out.product_id)
        product = existing_products.get(product_out.product_id)
        product_data = product_out.model_dump(exclude={"id", "work_id"})
        if product is None:
            movie.products.append(MovieProduct(**product_data))
            continue
        for field, value in product_data.items():
            setattr(product, field, value)

    for product in list(movie.products):
        if product.product_id not in incoming_product_ids:
            db.delete(product)

    refreshed_at = datetime.now()
    movie.source_type = AVBASE_DETAIL_SOURCE
    movie.last_seen_at = refreshed_at
    movie.metadata_updated_at = refreshed_at
    db.commit()
    db.refresh(movie)
    return _movie_data_out(movie)


async def refresh_information_by_work_id_service(
    db: Session,
    full_id: str,
    *,
    max_age: Optional[timedelta] = None,
) -> MovieDataOut:
    work_id = full_id.split(":", 1)[1] if ":" in full_id else full_id
    lock = _MOVIE_REFRESH_LOCKS[work_id.casefold()]

    async with lock:
        db.expire_all()
        movie = db.query(MovieData).filter(MovieData.work_id == work_id).first()
        if movie is not None and max_age is not None and _metadata_is_fresh(
            movie,
            max_age,
        ):
            return _movie_data_out(movie)

        try:
            return await _fetch_and_store_movie_information(db, full_id, movie)
        except Exception:
            db.rollback()
            raise


def _gen_movie_product(work_products: list[dict]) -> list[MovieProductOut]:
    results = []
    for product in work_products:
        results.append(
            MovieProductOut(
                product_id=product["product_id"],
                url=product["url"],
                image_url=product.get("image_url"),
                title=product.get("title"),
                source=product.get("source"),
                thumbnail_url=product.get("thumbnail_url"),
                date=parse_min_date(product.get("date")),
                maker=(
                    product.get("maker", {}).get("name")
                    if product.get("maker")
                    else None
                ),
                label=(
                    product.get("label", {}).get("name")
                    if product.get("label")
                    else None
                ),
                series=(
                    product.get("series", {}).get("name")
                    if product.get("series")
                    else None
                ),
                sample_image_urls=product.get("sample_image_urls", []),
                director=(
                    product.get("iteminfo", {}).get("director")
                    if product.get("iteminfo")
                    else None
                ),
                price=(
                    product.get("iteminfo", {}).get("price")
                    if product.get("iteminfo")
                    else None
                ),
                volume=(
                    product.get("iteminfo", {}).get("volume")
                    if product.get("iteminfo")
                    else None
                ),
            )
        )
    return results


def _gen_movie_data(work: dict) -> MovieDataOut:
    return MovieDataOut(
        work_id=work["work_id"],
        prefix=work.get("prefix", ""),
        title=work.get("title", ""),
        min_date=parse_min_date(work.get("min_date")),
        casts=[cast["actor"] for cast in work.get("casts", [])],
        actors=work.get("actors", []),
        tags=work.get("tags", []),
        genres=[genre["name"] for genre in work.get("genres", [])],
    )


async def _get_every_day_release(date_str: str) -> list[dict]:
    all_works = []
    page = 1
    while True:
        content = await avbase_client.fetch_html(
            f"{AVBASE_BASE_URL}/works/date/{date_str}?{urlencode({'page': page})}"
        )
        works = parse_release_works(content)
        if not works:
            break
        all_works.extend(works)
        page += 1
    return all_works


async def fetch_avbase_release_by_date_and_write_db(
    db: Session, date_str: str
) -> None:
    all_works = await _get_every_day_release(date_str)
    fetched_at = datetime.now()

    movie_records = [
        {
            "work_id": work["work_id"],
            "prefix": work.get("prefix", ""),
            "title": work.get("title", ""),
            "min_date": parse_min_date(work.get("min_date")),
            "casts": [cast["actor"] for cast in work.get("casts", [])],
            "actors": work.get("actors", []),
            "tags": work.get("tags", []),
            "genres": [genre["name"] for genre in work.get("genres", [])],
            "source_type": AVBASE_RELEASE_SOURCE,
            "last_seen_at": fetched_at,
        }
        for work in all_works
    ]

    if movie_records:
        stmt = sqlite_insert(MovieData).values(movie_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id"],
            set_={
                "prefix": stmt.excluded.prefix,
                "title": stmt.excluded.title,
                "min_date": stmt.excluded.min_date,
                "casts": stmt.excluded.casts,
                "actors": stmt.excluded.actors,
                "tags": stmt.excluded.tags,
                "genres": stmt.excluded.genres,
                "last_seen_at": stmt.excluded.last_seen_at,
            },
        )
        db.execute(stmt)
        db.flush()

    work_ids = [work["work_id"] for work in all_works]
    movie_map = {
        movie.work_id: movie.id
        for movie in db.query(MovieData).filter(MovieData.work_id.in_(work_ids)).all()
    }

    product_records = []
    for work in all_works:
        movie_id = movie_map[work["work_id"]]
        for product in work.get("products", []):
            product_records.append(
                {
                    "product_id": product["product_id"],
                    "url": product["url"],
                    "image_url": product.get("image_url"),
                    "title": product.get("title"),
                    "source": product.get("source"),
                    "thumbnail_url": product.get("thumbnail_url"),
                    "date": parse_min_date(product.get("date")),
                    "maker": (
                        product.get("maker", {}).get("name")
                        if product.get("maker")
                        else None
                    ),
                    "label": (
                        product.get("label", {}).get("name")
                        if product.get("label")
                        else None
                    ),
                    "series": (
                        product.get("series", {}).get("name")
                        if product.get("series")
                        else None
                    ),
                    "sample_image_urls": product.get("sample_image_urls", []),
                    "director": (
                        product.get("iteminfo", {}).get("director")
                        if product.get("iteminfo")
                        else None
                    ),
                    "price": (
                        product.get("iteminfo", {}).get("price")
                        if product.get("iteminfo")
                        else None
                    ),
                    "volume": (
                        product.get("iteminfo", {}).get("volume")
                        if product.get("iteminfo")
                        else None
                    ),
                    "work_id": movie_id,
                }
            )

    if product_records:
        stmt = sqlite_insert(MovieProduct).values(product_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id", "product_id"],
            set_={
                key: stmt.excluded[key]
                for key in product_records[0]
                if key != "work_id"
            },
        )
        db.execute(stmt)

    cache_stmt = sqlite_insert(AvbaseReleaseCache).values(
        release_date=date_str,
        fetched_at=fetched_at,
    )
    cache_stmt = cache_stmt.on_conflict_do_update(
        index_elements=["release_date"],
        set_={"fetched_at": cache_stmt.excluded.fetched_at},
    )
    db.execute(cache_stmt)
    db.commit()


def cleanup_avbase_release_cache(
    db: Session,
    *,
    retention_days: Optional[int] = None,
    batch_size: int = 500,
    now: Optional[datetime] = None,
) -> int:
    days = _release_retention_days() if retention_days is None else retention_days
    if days <= 0 or batch_size <= 0:
        return 0

    cutoff = (now or datetime.now()) - timedelta(days=days)
    deleted = 0

    while True:
        movie_ids = [
            movie_id
            for (movie_id,) in (
                db.query(MovieData.id)
                .outerjoin(
                    MovieSubscribe,
                    MovieSubscribe.movie_id == MovieData.id,
                )
                .filter(
                    MovieData.source_type == AVBASE_RELEASE_SOURCE,
                    MovieData.last_seen_at < cutoff,
                    MovieSubscribe.movie_id.is_(None),
                )
                .order_by(MovieData.id)
                .limit(batch_size)
                .all()
            )
        ]
        if not movie_ids:
            break

        db.query(MovieProduct).filter(
            MovieProduct.work_id.in_(movie_ids)
        ).delete(synchronize_session=False)
        db.query(MovieData).filter(MovieData.id.in_(movie_ids)).delete(
            synchronize_session=False
        )
        db.commit()
        deleted += len(movie_ids)

    expired_cache_dates = (
        db.query(AvbaseReleaseCache)
        .filter(AvbaseReleaseCache.fetched_at < cutoff)
        .delete(synchronize_session=False)
    )
    if expired_cache_dates:
        db.commit()

    db.commit()
    auto_vacuum_mode = int(
        db.execute(text("PRAGMA auto_vacuum")).scalar() or 0
    )
    if auto_vacuum_mode == 2:
        db.execute(text("PRAGMA incremental_vacuum"))
        db.commit()

    return deleted


def _release_cache_is_fresh(
    db: Session,
    date_str: str,
    *,
    retention_days: Optional[int] = None,
    now: Optional[datetime] = None,
) -> bool:
    days = _release_retention_days() if retention_days is None else retention_days
    query = db.query(AvbaseReleaseCache.release_date).filter(
        AvbaseReleaseCache.release_date == date_str
    )
    if days <= 0:
        return query.first() is not None

    cutoff = (now or datetime.now()) - timedelta(days=days)
    return query.filter(AvbaseReleaseCache.fetched_at >= cutoff).first() is not None


async def get_release_service(db: Session, date_str: str):
    if not _release_cache_is_fresh(db, date_str):
        await fetch_avbase_release_by_date_and_write_db(db, date_str)

    records = (
        db.query(MovieData)
        .options(selectinload(MovieData.products))
        .filter(MovieData.min_date == date_str)
        .all()
    )

    categorized: dict[str, list[dict]] = defaultdict(list)
    for movie in records:
        if not movie.products:
            continue

        movie_out = MovieDataOut.model_validate(movie)
        merged_product = _merge_products(movie_out.products)
        if merged_product is None:
            continue

        img_url = merged_product.image_url
        if not img_url and merged_product.thumbnail_url:
            img_url = merged_product.thumbnail_url.replace("ps.jpg", "pl.jpg")

        actor_names = {
            actor.get("name")
            for actor in (movie_out.actors + movie_out.casts)
            if actor.get("name")
        }
        poster = MoviePoster(
            id=movie.work_id,
            full_id=f"{movie_out.prefix}:{movie_out.work_id}",
            title=merged_product.title or movie_out.title,
            release_date=merged_product.date or movie_out.min_date or "",
            img_url=img_url or "",
            actors=list(actor_names),
        )
        categorized[merged_product.maker or "Unknown"].append(poster.model_dump())

    return [
        {"maker": maker, "works": works}
        for maker, works in sorted(
            categorized.items(), key=lambda item: len(item[1]), reverse=True
        )
    ]


def _merge_products(
    products: list[MovieProductOut],
) -> Optional[MovieProductOut]:
    if not products:
        return None

    merged = deepcopy(products[0])
    for product in products[1:]:
        for field, value in product.model_dump().items():
            current_value = getattr(merged, field)
            if isinstance(value, list):
                value = value or []
                current_value = current_value or []
                setattr(
                    merged,
                    field,
                    current_value + [item for item in value if item not in current_value],
                )
            elif (current_value is None or current_value == "") and value not in (
                None,
                "",
            ):
                setattr(merged, field, value)
    return merged
