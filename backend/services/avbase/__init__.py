from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote, urlencode

from fastapi import HTTPException
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, selectinload

from config import _config
from database import (
    ActorData,
    MovieData,
    MovieProduct,
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


def _cache_hours() -> float:
    try:
        return float(_config.get("AVBASE_ACTOR_CACHE_HOURS", 24))
    except (TypeError, ValueError):
        return 24.0


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
            record = ActorData(**data.model_dump())
            db.add(record)
        else:
            for key, value in data.model_dump().items():
                setattr(record, key, value)

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

    if not movie:
        encoded_id = quote(full_id, safe=":")
        content = await avbase_client.fetch_html(
            f"{AVBASE_BASE_URL}/works/{encoded_id}"
        )
        work = parse_movie_information(content)
        movie_out = _gen_movie_data(work)
        movie = MovieData(**movie_out.model_dump())
        db.add(movie)
        db.flush()

        db_products = []
        for product_out in _gen_movie_product(work.get("products", [])):
            product_data = product_out.model_dump()
            product_data["work_id"] = movie.id
            db_products.append(MovieProduct(**product_data))

        db.add_all(db_products)
        db.commit()
        db.refresh(movie)

    movie_out = MovieDataOut.model_validate(movie)
    merged_product = _merge_products(movie_out.products)
    if merged_product is None:
        raise HTTPException(status_code=502, detail="作品缺少产品信息")

    if not merged_product.image_url and merged_product.thumbnail_url:
        merged_product.image_url = merged_product.thumbnail_url.replace(
            "ps.jpg", "pl.jpg"
        )

    movie_out.products = [merged_product]
    return movie_out


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
    db.commit()


async def get_release_service(db: Session, date_str: str):
    records = (
        db.query(MovieData)
        .options(selectinload(MovieData.products))
        .filter(MovieData.min_date == date_str)
        .all()
    )
    if not records:
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
