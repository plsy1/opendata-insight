from fastapi import APIRouter, HTTPException, Depends, Body, Query, BackgroundTasks
from services.auth import tokenInterceptor
from fastapi.responses import StreamingResponse
from services.task import *
from services.system import *
from config import _config

router = APIRouter()


@router.get("/get_image")
async def get_image(token: str = Query(...)):
    """
    token: 加密后的图片访问 token
    """

    try:
        payload: DecryptedImagePayload = decrypt_payload(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token")

    import time

    if payload.exp < int(time.time()):
        raise HTTPException(status_code=403, detail="Token expired")

    content, headers = await fetch_and_cache_image(payload.url)

    return StreamingResponse(content, media_type="image/jpeg", headers=headers)


@router.get("/getEnvironment")
async def get_app_environment(isValid: str = Depends(tokenInterceptor)):
    return _config.get_environment()


@router.post("/updateEnvironment")
async def update_environment(
    env: dict = Body(...), isValid: str = Depends(tokenInterceptor)
):
    try:
        _config.set(env)
        return {"success": True, "message": "Environment updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh_emby_movies_database")
async def update(isValid: str = Depends(tokenInterceptor)):
    update_emby_movies_in_db()


@router.post("/refreshKeywordsFeeds")
async def refresh_keywords(
    isValid: str = Depends(tokenInterceptor), background_tasks: BackgroundTasks = None
):
    try:
        background_tasks.add_task(refresh_movies_feeds)
        return {"message": "Feeds refreshed and torrents added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


@router.post("/refreshActressFeeds")
async def refresh_actress(
    isValid: str = Depends(tokenInterceptor), background_tasks: BackgroundTasks = None
):
    try:
        background_tasks.add_task(refresh_actress_feeds)
        return {"message": "Actress Feeds refreshed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


@router.post("/refreshFC2Metadata")
async def refresh_actress(background_tasks: BackgroundTasks = None):
    try:
        background_tasks.add_task(update_fc2_ranking_in_db)
        return {"message": "Fc2 Metadata refresh started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
