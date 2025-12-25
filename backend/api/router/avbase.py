from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from modules.metadata.avbase import *
from core.config import _config


router = APIRouter()


@router.get("/actress/movies")
async def get_actress_movies(
    name: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    movies = await get_movie_info_by_actress_name(name, page)
    return {"movies": movies, "page": page}


@router.get("/actress/information")
async def get_actress_information(name: str, isValid: str = Depends(tokenInterceptor)):
    from core.database import ActorData, get_db

    db = next(get_db())

    import urllib.parse

    name = urllib.parse.unquote(name)

    try:
        result = db.query(ActorData).where(ActorData.name == name).first()

        if result:
            result_dict = {
                k: v
                for k, v in result.__dict__.items()
                if not k.startswith("_sa_instance_state")
            }
            new_result = replace_domain_in_value(
                result_dict, _config.get("SYSTEM_IMAGE_PREFIX"),['x.com','www.instagram.com','www.avbase.net','ja.wikipedia.org','www.tiktok.com']
            )
            return new_result

        actress_data = await get_actress_info_by_actress_name(name)
        if not actress_data:
            return {"error": "Actor not found"}

        new_actor = ActorData(
            **actress_data.dict(exclude={"raw_avatar_url"}),
            isSubscribe=False,
            isCollect=False,
        )
        db.add(new_actor)
        db.commit()
        db.refresh(new_actor)

        return replace_domain_in_value(new_actor, _config.get("SYSTEM_IMAGE_PREFIX"))

    except Exception as e:
        return {"error": str(e)}


@router.get("/movie/information")
async def get_information_by_work_id(
    work_id: str, isValid: str = Depends(tokenInterceptor)
):
    from modules.metadata.avbase import get_information_by_work_id as func
    from urllib.parse import unquote

    result = await func(unquote(work_id))

    return replace_domain_in_value(result, _config.get("SYSTEM_IMAGE_PREFIX"))


@router.get("/keywords")
async def search_movies_by_keywords(
    keywords: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    return await get_movie_info_by_keywords(keywords, page)


@router.get("/get_index")
async def get_index_data(isValid: str = Depends(tokenInterceptor)):
    from core.database import get_db, avbaseNewbie, avbasePopular
    from modules.metadata.avbase import fetch_avbase_index_actor_list

    try:
        db = next(get_db())

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

        return replace_domain_in_value(result, _config.get("SYSTEM_IMAGE_PREFIX"))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取失败: {e}")
    finally:
        db.close()
