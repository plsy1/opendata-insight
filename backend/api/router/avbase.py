from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from core.config import _config
from modules.metadata.avbase import *
from core.database import get_db, AvbaseReleaseEveryday

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
async def get_movie_information(url: str, isValid: str = Depends(tokenInterceptor)):
    return await get_actors_from_work(url)


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

    record_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    db = next(get_db())
    try:
        record = (
            db.query(AvbaseReleaseEveryday)
            .filter(AvbaseReleaseEveryday.date == record_date)
            .first()
        )

        SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")

        if record:
            result = json.loads(record.data_json)
            result = replace_domain_in_value(result, SYSTEM_IMAGE_PREFIX)
            return result

        result = await get_release_grouped_by_prefix(date_str, False)

        json_data = json.dumps(
            [r.model_dump() for r in result], ensure_ascii=False, default=str
        )

        new_record = AvbaseReleaseEveryday(date=record_date, data_json=json_data)
        db.add(new_record)
        db.commit()

        return replace_domain_in_value(result, SYSTEM_IMAGE_PREFIX)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取失败: {e}")
    finally:
        db.close()
