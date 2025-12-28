from fastapi import APIRouter, HTTPException, Depends, Body, Query, Response, status
from services.auth import tokenInterceptor
from fastapi.responses import StreamingResponse
from services.system import *
from config import _config

router = APIRouter()


@router.get("/get_image")
async def get_image(token: str = Query(...)):
    try:
        payload: DecryptedImagePayload = decrypt_payload(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token")
    import time
    if payload.exp < int(time.time()):
        raise HTTPException(status_code=403, detail="Token expired")
    content, headers = await fetch_and_cache_image(payload.url)
    return StreamingResponse(content, media_type="image/jpeg", headers=headers)


@router.get("/get_environment")
async def get_app_environment(isValid: str = Depends(tokenInterceptor)):
    return _config.get_environment()

@router.post("/update_environment")
async def update_environment(
    env: dict = Body(...), isValid: str = Depends(tokenInterceptor)
):
    try:
        _config.set(env)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
