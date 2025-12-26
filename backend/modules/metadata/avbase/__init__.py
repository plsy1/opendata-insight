import json
from bs4 import BeautifulSoup
from typing import List
from .model import *
from .helper import *
from core.config import _config
from core.system import replace_domain_in_value, encrypt_payload
from core.system.model import DecryptedImagePayload
import time
from sqlalchemy.dialects.sqlite import insert as sqlite_insert


async def get_actress_info_by_actress_name(name: str) -> Actress:
    actress = Actress(name=name)

    url = f"https://www.avbase.net/talents/{name}"
    content = await get_raw_html(url)

    soup = BeautifulSoup(content, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        data = json.loads(script_tag.string)
        page_props = data["props"]["pageProps"]
        talent = page_props.get("talent", {})

        primary = talent.get("primary", {})

        actress.avatar_url = f'{primary.get("image_url")}'

        fanza = (primary.get("meta") or {}).get("fanza") or {}
        for k, v in fanza.items():
            if hasattr(actress, k):
                setattr(actress, k, v)

        actors = talent.get("actors", [])
        actress.aliases = [actor.get("name") for actor in actors if actor.get("name")]

    actress.social_media = get_social_media_links(soup)

    return actress


async def get_movie_info_by_actress_name(
    name: str, page: int, changeImagePrefix: bool = True
) -> List[Movie]:
    url = f"https://www.avbase.net/talents/{name}?q=&page={page}"
    return await get_movies(url, changeImagePrefix=changeImagePrefix)


async def get_movie_info_by_keywords(keywords: str, page: int) -> List[Movie]:
    url = f"https://www.avbase.net/works?q={keywords}&page={page}"
    return await get_movies(url)


async def fetch_avbase_index_actor_list():

    from core.database import get_db, avbaseNewbie, avbasePopular

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


async def get_information_by_work_id(canonical_id: str) -> MovieDataOut:

    from core.database import MovieData, MovieProduct, get_db

    db = next(get_db())

    if ":" in canonical_id:
        work_id = canonical_id.split(":", 1)[1]
    else:
        work_id = canonical_id

    movie = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    if not movie:
        url = f"https://www.avbase.net/works/{canonical_id}"

        data = await get_next_data(url)

        work = data.get("props", {}).get("pageProps", {}).get("work", {})

        min_date = parse_min_date(work.get("date"))

        movie = MovieData(
            work_id=work["work_id"],
            prefix=work.get("prefix", ""),
            title=work.get("title", ""),
            min_date=min_date,
            casts=[c["actor"] for c in work.get("casts", [])],
            actors=work.get("actors", []),
            tags=work.get("tags", []),
            genres=[g["name"] for g in work.get("genres", [])],
        )
        db.add(movie)
        db.flush()

        for p in work.get("products", []):
            min_date = parse_min_date(p.get("date"))
            product_data = dict(
                product_id=p["product_id"],
                url=p["url"],
                image_url=p.get("image_url"),
                title=p.get("title"),
                source=p.get("source"),
                thumbnail_url=p.get("thumbnail_url"),
                date=min_date,
                maker=p.get("maker", {}).get("name") if p.get("maker") else None,
                label=p.get("label", {}).get("name") if p.get("label") else None,
                series=p.get("series", {}).get("name") if p.get("series") else None,
                sample_image_urls=p.get("sample_image_urls", []),
                director=(
                    p.get("iteminfo", {}).get("director") if p.get("iteminfo") else None
                ),
                price=p.get("iteminfo", {}).get("price") if p.get("iteminfo") else None,
                volume=(
                    p.get("iteminfo", {}).get("volume") if p.get("iteminfo") else None
                ),
                work_id=movie.id,
            )

            product = MovieProduct(**product_data)
            db.add(product)

        db.commit()

        db.refresh(movie)

    movie_out = MovieDataOut.model_validate(movie)
    movie_out_dict = movie_out.model_dump()

    def merge_products(products: list[dict]) -> dict:
        merged = {}
        for p in products:
            for key, value in p.items():
                if (value is not None and not (isinstance(value, list) and len(value) == 0)) and key not in merged:
                    merged[key] = value
        return merged

    if "products" in movie_out_dict and isinstance(movie_out_dict["products"], list):
        merged_product = merge_products(movie_out_dict["products"])
        # 这里注意要用列表包起来
        movie_out_dict["products"] = [merged_product]

    movie_out = MovieDataOut(**movie_out_dict)
    if not movie_out.products[0].image_url:
        movie_out.products[0].image_url = movie_out.products[0].thumbnail_url.replace("ps.jpg","pl.jpg")
    return movie_out


async def get_release_by_date(date_str: str):
    """
    获取指定日期的作品列表，写入数据库
    date_str: 'YYYY-MM-DD'
    """

    from core.database import MovieData, MovieProduct, get_db

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

    # ----------- 准备 MovieData 批量数据 -----------
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

    # ----------- 批量 upsert MovieData -----------
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

    # ----------- 获取 work_id -> movie.id 映射 -----------
    work_ids = [w["work_id"] for w in all_works]
    movie_map = {
        m.work_id: m.id
        for m in db.query(MovieData).filter(MovieData.work_id.in_(work_ids)).all()
    }

    # ----------- 准备 MovieProduct 批量数据 -----------
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

    # ----------- 批量 upsert MovieProduct -----------
    if product_records:
        stmt = sqlite_insert(MovieProduct).values(product_records)
        # UPSERT 按 (work_id, product_id) 唯一约束
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id", "product_id"],
            set_={
                k: stmt.excluded[k] for k in product_records[0].keys() if k != "work_id"
            },
        )
        db.execute(stmt)

    db.commit()
