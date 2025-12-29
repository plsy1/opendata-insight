from modules.metadata.avbase import *
from schemas.actor import ActorDataOut, AvbaseIndexActorOut
from schemas.movies import MovieDataOut, MovieProductOut
from sqlalchemy.orm import Session
from database import ActorData, avbaseNewbie, avbasePopular, MovieData, MovieProduct
from sqlalchemy.orm import selectinload


async def get_movie_list_by_actor_name_service(
    name: str, page: int
) -> list[MoviePoster]:
    url = f"https://www.avbase.net/talents/{name}?q=&page={page}"
    return await parse_movie_lists(url)


async def get_movie_list_by_keywords_service(
    keywords: str, page: int
) -> list[MoviePoster]:
    url = f"https://www.avbase.net/works?q={keywords}&page={page}"
    return await parse_movie_lists(url)


async def get_actor_information_by_name_service(db: Session, name: str) -> ActorDataOut:

    records = db.query(ActorData).where(ActorData.name == name).first()

    if not records:
        url = f"https://www.avbase.net/talents/{name}"
        data = await parse_actor_information(url)
        new_actor = ActorData(**data.model_dump())
        db.add(new_actor)
        db.commit()
        db.refresh(new_actor)

        records = new_actor

    return ActorDataOut.model_validate(records)


async def get_avbase_index_actor_service(db: Session):
    newbie_records = db.query(avbaseNewbie).all()
    popular_records = db.query(avbasePopular).all()

    if not newbie_records or not popular_records:
        newbie_data_list, popular_data_list = await parse_actor_lists()

        newbie_records = [
            avbaseNewbie(name=a.name, avatar_url=a.avatar_url) for a in newbie_data_list
        ]
        popular_records = [
            avbasePopular(name=a.name, avatar_url=a.avatar_url)
            for a in popular_data_list
        ]

        db.add_all(newbie_records)
        db.add_all(popular_records)
        db.commit()

        for record in newbie_records + popular_records:
            db.refresh(record)

    result = {
        "newbie_talents": [
            AvbaseIndexActorOut.model_validate(r) for r in newbie_records
        ],
        "popular_talents": [
            AvbaseIndexActorOut.model_validate(r) for r in popular_records
        ],
    }

    return result


async def get_information_by_work_id_service(db: Session, full_id: str) -> MovieDataOut:

    work_id = full_id.split(":", 1)[1] if ":" in full_id else full_id

    movie = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    if not movie:
        work = await parse_movie_information(full_id)
        movie_out = _gen_movie_data(work)
        movie = MovieData(**movie_out.model_dump())
        db.add(movie)
        db.flush()
        products_list = _gen_movie_product(work.get("products", []))
        db_products = []
        for product_out in products_list:
            product_data = product_out.model_dump()
            product_data["work_id"] = movie.id
            db_products.append(MovieProduct(**product_data))

        db.add_all(db_products)
        db.commit()
        db.refresh(movie)

    movie_out = MovieDataOut.model_validate(movie)

    if not movie_out.products[0].image_url:
        movie_out.products[0].image_url = movie_out.products[0].thumbnail_url.replace(
            "ps.jpg", "pl.jpg"
        )

    return movie_out


def _gen_movie_product(work_products: list[dict]) -> list[MovieProductOut]:

    results: list[MovieProductOut] = []

    for p in work_products:
        product_out = MovieProductOut(
            product_id=p["product_id"],
            url=p["url"],
            image_url=p.get("image_url"),
            title=p.get("title"),
            source=p.get("source"),
            thumbnail_url=p.get("thumbnail_url"),
            date=parse_min_date(p.get("date")),
            maker=p.get("maker", {}).get("name") if p.get("maker") else None,
            label=p.get("label", {}).get("name") if p.get("label") else None,
            series=p.get("series", {}).get("name") if p.get("series") else None,
            sample_image_urls=p.get("sample_image_urls", []),
            director=(
                p.get("iteminfo", {}).get("director") if p.get("iteminfo") else None
            ),
            price=p.get("iteminfo", {}).get("price") if p.get("iteminfo") else None,
            volume=p.get("iteminfo", {}).get("volume") if p.get("iteminfo") else None,
        )

        results.append(product_out)

    return results


def _gen_movie_data(work: dict) -> MovieDataOut:
    return MovieDataOut(
        work_id=work["work_id"],
        prefix=work.get("prefix", ""),
        title=work.get("title", ""),
        min_date=parse_min_date(work.get("min_date")),
        casts=[c["actor"] for c in work.get("casts", [])],
        actors=work.get("actors", []),
        tags=work.get("tags", []),
        genres=[g["name"] for g in work.get("genres", [])],
    )


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

    from collections import defaultdict

    categorized: dict[str, list[dict]] = defaultdict(list)

    for movie in records:
        if not movie.products:
            continue

        movie_out = MovieDataOut.model_validate(movie)

        first_product = movie_out.products[0]

        maker = first_product.maker or "Unknown"

        movie_out.products = [first_product]

        categorized[maker].append(movie_out.model_dump())

    result = [
        {"maker": maker, "works": works}
        for maker, works in sorted(
            categorized.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )
    ]

    for group in result:
        for work in group["works"]:
            p = work["products"][0]
            if not p.get("image_url") and p.get("thumbnail_url"):
                p["image_url"] = p["thumbnail_url"].replace("ps.jpg", "pl.jpg")

    return result
