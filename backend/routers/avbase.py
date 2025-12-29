from fastapi import APIRouter, Depends, HTTPException
from services.auth import tokenInterceptor
from modules.metadata.avbase import *
from services.system import replace_domain_in_value
from schemas.movies import MovieDataOut
from config import _config
from urllib.parse import unquote
from sqlalchemy.orm import selectinload
from database import get_db, avbaseNewbie, avbasePopular, MovieData
from sqlalchemy.orm import Session
from services.avbase import *


router = APIRouter()

@router.get("/get_index")
async def get_avbase_index_actor(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        return await get_avbase_index_actor_service(db)

    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.get("/search")
async def get_movie_list_by_keywords(
    keywords: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    try:
        return await get_movie_list_by_keywords_service(keywords, page)
    except Exception as e:
        return {"error": str(e)}


@router.get("/moviesOfActor")
async def get_movie_list_by_actor_name(
    name: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    try:
        return await get_movie_list_by_actor_name_service(name, page)
    except Exception as e:
        return {"error": str(e)}


@router.get("/actorInformation")
async def get_actor_information_by_name(
    name: str, db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        return await get_actor_information_by_name_service(db, name)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}



@router.get("/movieInformation")
async def get_movie_information(work_id: str, isValid: str = Depends(tokenInterceptor)):
    try:
        result = await get_information_by_work_id(unquote(work_id), True)
        return result
    except Exception as e:
        return {"error": str(e)}



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
        await fetch_avbase_release_by_date_and_write_db(date_str)
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
