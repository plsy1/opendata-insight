from fastapi import APIRouter, Depends, HTTPException
from services.auth import tokenInterceptor
from modules.metadata.avbase import (
    get_movie_info_by_actress_name,
    get_actress_info_by_actress_name,
    get_information_by_work_id,
    get_movie_info_by_keywords,
    fetch_avbase_index_actor_list,
    get_release_by_date,
)
from services.system import replace_domain_in_value
from schemas.movies import MovieDataOut
from config import _config
from urllib.parse import unquote
from sqlalchemy.orm import selectinload
from database import get_db, avbaseNewbie, avbasePopular, MovieData
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/moviesOfActor")
async def get_movies_of_actor(
    name: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    movies = await get_movie_info_by_actress_name(name, page, True)
    return {"movies": movies, "page": page}


@router.get("/actorInformation")
async def get_actor_information(name: str, isValid: str = Depends(tokenInterceptor)):
    try:
        return await get_actress_info_by_actress_name(name, True)
    except Exception as e:
        return {"error": str(e)}


@router.get("/movieInformation")
async def get_movie_information(work_id: str, isValid: str = Depends(tokenInterceptor)):

    result = await get_information_by_work_id(unquote(work_id), True)

    return result


@router.get("/search")
async def search_movies_by_keywords(
    keywords: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    return await get_movie_info_by_keywords(keywords, page, True)


@router.get("/get_index")
async def get_index_data(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:

        newbie_records = db.query(avbaseNewbie).filter_by(isActive=True).all()
        popular_records = db.query(avbasePopular).filter_by(isActive=True).all()

        if not newbie_records:
            await fetch_avbase_index_actor_list()
            newbie_records = db.query(avbaseNewbie).filter_by(isActive=True).all()
            popular_records = db.query(avbasePopular).filter_by(isActive=True).all()

        newbie = [
            {
                k: v
                for k, v in r.__dict__.items()
                if k != "isActive" and not k.startswith("_sa_instance_state")
            }
            for r in newbie_records
        ]
        popular = [
            {
                k: v
                for k, v in r.__dict__.items()
                if k != "isActive" and not k.startswith("_sa_instance_state")
            }
            for r in popular_records
        ]

        result = {"newbie_talents": newbie, "popular_talents": popular}

        return replace_domain_in_value(result, _config.get("SYSTEM_IMAGE_PREFIX"))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取失败: {e}")
    finally:
        db.close()


@router.get("/get_release_by_date")
async def get_release(
    yyyymmdd: str,
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):

    if len(yyyymmdd) != 8 or not yyyymmdd.isdigit():
        raise HTTPException(
            status_code=400, detail="Date format error. Expected format: YYYYMMDD."
        )

    date_str = f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"

    records = (
        db.query(MovieData)
        .options(selectinload(MovieData.products))
        .filter(MovieData.min_date == date_str)
        .all()
    )

    if not records:
        await get_release_by_date(date_str)
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

    return replace_domain_in_value(
        result,
        _config.get("SYSTEM_IMAGE_PREFIX"),
    )
