from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.emby import *
from database import get_db
from services.system import replace_domain_in_value

router = APIRouter()


@router.get("/get_item_counts")
async def get_item_counts():
    try:
        result = await get_item_counts_service()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_resume")
async def get_resume():
    try:
        result = await get_resume_items_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_latest")
async def get_latest():
    try:
        result = await get_latest_items_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_views")
async def get_latest():
    try:
        result = await get_views_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/get_all")
async def get_latest():
    try:
        result = await get_all_movies_service()
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")


@router.get("/exists")
async def exists(
    title: str, db: Session = Depends(get_db), 
):
    try:
        result = await exists_service(db, title)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}")
