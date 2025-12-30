from fastapi import APIRouter, HTTPException, Body, Query, Response, status, Depends
from fastapi.responses import StreamingResponse
from services.system import *
from config import _config
from .dependencies.auth_dependencies import token_interceptor

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
async def get_app_environment(dep: None = Depends(token_interceptor)):
    return _config.get_environment()


@router.post("/update_environment")
async def update_environment(
    env: dict = Body(...), dep: None = Depends(token_interceptor)
):
    try:
        _config.set(env)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
