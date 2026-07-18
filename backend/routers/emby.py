from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.emby import *
from database import get_db
from services.system import replace_domain_in_value
from schemas.emby import EmbyExistsOut, EmbyMediaItemOut

router = APIRouter()


@router.get("/get_item_counts", response_model=dict[str, int])
async def get_item_counts():
    try:
        result = await get_item_counts_service()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_resume", response_model=list[EmbyMediaItemOut])
async def get_resume():
    try:
        result = await get_resume_items_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_latest", response_model=list[EmbyMediaItemOut])
async def get_latest():
    try:
        result = await get_latest_items_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_views", response_model=list[EmbyMediaItemOut])
async def get_latest():
    try:
        result = await get_views_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_all", response_model=list[EmbyMediaItemOut])
async def get_latest():
    try:
        result = await get_all_movies_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/exists", response_model=EmbyExistsOut)
async def exists(
    title: str, db: Session = Depends(get_db), 
):
    try:
        result = await exists_service(db, title)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")
