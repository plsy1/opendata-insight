from fastapi import APIRouter, Depends, HTTPException
from services.auth import tokenInterceptor
from modules.metadata.avbase import *
from services.system import replace_domain_in_value
from urllib.parse import unquote
from database import get_db
from sqlalchemy.orm import Session
from services.avbase import *


router = APIRouter()


@router.get("/get_index")
async def get_avbase_index_actor(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        result = await get_avbase_index_actor_service(db)
        return replace_domain_in_value(result)

    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.get("/search")
async def get_movie_list_by_keywords(
    keywords: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    try:
        result = await get_movie_list_by_keywords_service(keywords, page)
        return replace_domain_in_value(result)
    except Exception as e:
        return {"error": str(e)}


@router.get("/moviesOfActor")
async def get_movie_list_by_actor_name(
    name: str, page: int, isValid: str = Depends(tokenInterceptor)
):
    try:
        result = await get_movie_list_by_actor_name_service(name, page)
        return replace_domain_in_value(result)
    except Exception as e:
        return {"error": str(e)}


@router.get("/actorInformation")
async def get_actor_information_by_name(
    name: str, db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        result = await get_actor_information_by_name_service(db, name)
        return replace_domain_in_value(result)
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.get("/movieInformation")
async def get_information_by_work_id(
    work_id: str,
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    try:
        work_id = unquote(work_id)
        result = await get_information_by_work_id_service(db, work_id)
        return replace_domain_in_value(result)
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

    result = await get_release_service(db, date_str)
    return replace_domain_in_value(result)
