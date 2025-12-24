from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from modules.metadata.avbase import *


router = APIRouter()


@router.get("/actress/movies")
async def get_actress_movies(
    name: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    movies = await get_movie_info_by_actress_name(name, page)
    return {"movies": movies, "page": page}


@router.get("/actress/information")
async def get_actress_information(name: str, isValid: str = Depends(tokenInterceptor)):
    return await get_actress_info_by_actress_name(name)


@router.get("/movie/information")
async def get_information_by_work_id(
    work_id: str, isValid: str = Depends(tokenInterceptor)
):
    from modules.metadata.avbase import get_information_by_work_id as func
    from urllib.parse import unquote

    return await func(unquote(work_id))


@router.get("/keywords")
async def search_movies_by_keywords(
    keywords: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    return await get_movie_info_by_keywords(keywords, page)


@router.get("/get_index")
async def get_index_data(isValid: str = Depends(tokenInterceptor)):
    return await get_index()


@router.get("/get_release_by_date")
async def get_relesae(yyyymmdd: str, isValid: str = Depends(tokenInterceptor)):
    if len(yyyymmdd) != 8 or not yyyymmdd.isdigit():
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYYMMDD")

    date_str = f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"

    from core.database import MovieData, get_db

    db = next(get_db())
    try:
        records = db.query(MovieData).filter(MovieData.min_date == date_str).all()

        if not records:
            await get_release_by_date(date_str)
            records = db.query(MovieData).filter(MovieData.min_date == date_str).all()

        from typing import Dict
        from collections import defaultdict

        categorized: Dict[str, List] = defaultdict(list)

        for movie in records:

            products = []

            products.append(
                {
                    "product_id": movie.products[0].product_id,
                    "url": movie.products[0].url,
                    "image_url": movie.products[0].image_url,
                    "title": movie.products[0].title,
                    "source": movie.products[0].source,
                    "thumbnail_url": movie.products[0].thumbnail_url,
                    "date": movie.products[0].date,
                    "maker": movie.products[0].maker,
                    "label": movie.products[0].label,
                    "series": movie.products[0].series,
                    "sample_image_urls": movie.products[0].sample_image_urls,
                    "director": movie.products[0].director,
                    "price": movie.products[0].price,
                    "volume": movie.products[0].volume,
                    "work_id": movie.products[0].work_id,
                }
            )

            work_data = {
                "id": movie.id,
                "prefix": movie.prefix,
                "work_id": movie.work_id,
                "title": movie.title,
                "min_date": movie.min_date,
                "casts": movie.casts,
                "actors": movie.actors,
                "tags": movie.tags,
                "genres": movie.genres,
                "products": products,
            }

            makers = set(p["maker"] for p in products if p["maker"])
            if not makers:
                makers = {"Unknown"}

            for maker in makers:
                categorized[maker].append(work_data)

        result = []
        for maker_name, works in sorted(
            categorized.items(), key=lambda x: len(x[1]), reverse=True
        ):
            result.append({"prefixName": maker_name, "works": works})

        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取失败: {e}")
    finally:
        db.close()
