import json
from bs4 import BeautifulSoup
from typing import List
from .helper import *
from config import _config
from services.system import replace_domain_in_value
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from schemas.actor import ActorDataOut
from schemas.movies import MovieDataOut
from database import MovieData, MovieProduct, get_db
from pydantic import BaseModel
from sqlalchemy.orm import Session


class Movie(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str]


async def get_actress_info_by_actress_name(
    name: str, changeImagePrefix: bool = False
) -> ActorDataOut:

    from database import get_db, ActorData

    db = next(get_db())

    records = db.query(ActorData).where(ActorData.name == name).first()

    if not records:
        data = ActorDataOut(name=name)

        url = f"https://www.avbase.net/talents/{name}"
        content = await get_raw_html(url)

        soup = BeautifulSoup(content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag:
            tmp = json.loads(script_tag.string)
            page_props = tmp["props"]["pageProps"]
            talent = page_props.get("talent", {})
            primary = talent.get("primary", {})
            data.avatar_url = f'{primary.get("image_url")}'
            fanza = (primary.get("meta") or {}).get("fanza") or {}
            for k, v in fanza.items():
                if hasattr(data, k):
                    setattr(data, k, v)

            actors = talent.get("actors", [])
            data.aliases = [actor.get("name") for actor in actors if actor.get("name")]

        data.social_media = get_social_media_links(soup)

        new_actor = ActorData(**data.model_dump())
        db.add(new_actor)
        db.commit()
        db.refresh(new_actor)

        records = new_actor

    if changeImagePrefix:
        records = replace_domain_in_value(records, _config.get("SYSTEM_IMAGE_PREFIX"))
    return ActorDataOut.model_validate(records)


async def get_movie_info_by_actress_name(
    name: str, page: int, changeImagePrefix: bool = False
) -> List[Movie]:
    url = f"https://www.avbase.net/talents/{name}?q=&page={page}"
    return await get_movies(url, changeImagePrefix=changeImagePrefix)


async def get_movie_info_by_keywords(
    keywords: str, page: int, changeImagePrefix: bool = False
) -> List[Movie]:
    url = f"https://www.avbase.net/works?q={keywords}&page={page}"
    return await get_movies(url, changeImagePrefix=changeImagePrefix)


async def fetch_avbase_index_actor_list():

    from database import get_db, avbaseNewbie, avbasePopular

    url = f"https://www.avbase.net"
    data = await get_next_data(url)
    data = data.get("props").get("pageProps")

    newbie_talents = data.get("newbie_talents")
    popular_talents = data.get("popular_talents")

    db = next(get_db())

    db.query(avbaseNewbie).update({avbaseNewbie.isActive: False})
    db.query(avbasePopular).update({avbasePopular.isActive: False})
    db.commit()

    for item in newbie_talents:
        for actor in item.get("actors", []):
            name = actor.get("name")
            avatar_url = actor.get("image_url")

            record = db.query(avbaseNewbie).filter_by(name=name).first()

            if record:
                record.avatar_url = avatar_url
                record.isActive = True
            else:
                record = avbaseNewbie(name=name, avatar_url=avatar_url, isActive=True)
                db.add(record)

    for item in popular_talents:
        actors = item.get("actors", [])
        if not actors:
            continue

        actor = actors[0]
        name = actor.get("name")
        avatar_url = actor.get("image_url")

        record = db.query(avbasePopular).filter_by(name=name).first()

        if record:
            record.avatar_url = avatar_url
            record.isActive = True
        else:
            record = avbasePopular(name=name, avatar_url=avatar_url, isActive=True)
            db.add(record)

    db.commit()


async def fetch_avbase_release_by_date_and_write_db(date_str: str):
    from database import MovieData, MovieProduct, get_db

    all_works = []

    page = 1
    while True:
        url = f"https://www.avbase.net/works/date/{date_str}?page={page}"
        data = await get_next_data(url)

        works_data = data.get("props", {}).get("pageProps", {}).get("works", [])

        if not works_data:
            break

        all_works.extend(works_data)
        page += 1

    db = next(get_db())

    movie_records = []
    for work_dict in all_works:
        min_date = parse_min_date(work_dict.get("min_date"))

        movie_records.append(
            dict(
                work_id=work_dict["work_id"],
                prefix=work_dict.get("prefix", ""),
                title=work_dict.get("title", ""),
                min_date=min_date,
                casts=[c["actor"] for c in work_dict.get("casts", [])],
                actors=work_dict.get("actors", []),
                tags=work_dict.get("tags", []),
                genres=[g["name"] for g in work_dict.get("genres", [])],
            )
        )

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

    work_ids = [w["work_id"] for w in all_works]
    movie_map = {
        m.work_id: m.id
        for m in db.query(MovieData).filter(MovieData.work_id.in_(work_ids)).all()
    }

    product_records = []
    for work_dict in all_works:
        movie_id = movie_map[work_dict["work_id"]]
        for p in work_dict.get("products", []):
            product_date = parse_min_date(p.get("date"))
            product_records.append(
                dict(
                    product_id=p["product_id"],
                    url=p["url"],
                    image_url=p.get("image_url"),
                    title=p.get("title"),
                    source=p.get("source"),
                    thumbnail_url=p.get("thumbnail_url"),
                    date=product_date,
                    maker=p.get("maker", {}).get("name") if p.get("maker") else None,
                    label=p.get("label", {}).get("name") if p.get("label") else None,
                    series=p.get("series", {}).get("name") if p.get("series") else None,
                    sample_image_urls=p.get("sample_image_urls", []),
                    director=(
                        p.get("iteminfo", {}).get("director")
                        if p.get("iteminfo")
                        else None
                    ),
                    price=(
                        p.get("iteminfo", {}).get("price")
                        if p.get("iteminfo")
                        else None
                    ),
                    volume=(
                        p.get("iteminfo", {}).get("volume")
                        if p.get("iteminfo")
                        else None
                    ),
                    work_id=movie_id,
                )
            )

    if product_records:
        stmt = sqlite_insert(MovieProduct).values(product_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id", "product_id"],
            set_={
                k: stmt.excluded[k] for k in product_records[0].keys() if k != "work_id"
            },
        )
        db.execute(stmt)

    db.commit()


async def get_information_by_work_id(
    canonical_id: str, changeImagePrefix: bool = False
) -> MovieDataOut:

    db = next(get_db())

    work_id = canonical_id.split(":", 1)[1] if ":" in canonical_id else canonical_id

    movie = get_movie_from_db(db, work_id)

    if not movie:
        work = await fetch_work_data(canonical_id)
        movie = parse_work_to_movie(work)
        db.add(movie)
        db.flush()
        add_products_to_db(db, work.get("products", []), movie.id)
        db.commit()
        db.refresh(movie)

    movie_out = MovieDataOut.model_validate(movie)
    movie_out_dict = movie_out.model_dump()

    if "products" in movie_out_dict and isinstance(movie_out_dict["products"], list):
        merged_product = merge_products(movie_out_dict["products"])
        movie_out_dict["products"] = [merged_product]

    movie_out = MovieDataOut(**movie_out_dict)

    if not movie_out.products[0].image_url:
        movie_out.products[0].image_url = movie_out.products[0].thumbnail_url.replace(
            "ps.jpg", "pl.jpg"
        )

    if changeImagePrefix:
        movie_out = replace_domain_in_value(
            movie_out, _config.get("SYSTEM_IMAGE_PREFIX")
        )

    return movie_out


async def fetch_movie_data_and_save_to_db(db: Session, full_id: str):

    work_id = full_id.split(":", 1)[1] if ":" in full_id else full_id

    records = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    if records:
        return

    work = await fetch_work_data(full_id)
    movie = parse_work_to_movie(work)
    db.add(movie)
    db.flush()
    add_products_to_db(db, work.get("products", []), movie.id)
    db.commit()
    db.refresh(movie)
