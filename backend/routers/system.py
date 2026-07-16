import os
import time
import httpx
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import _config
from database import get_db
from services.system import (
    CACHE_CONTROL,
    CachedImage,
    decrypt_payload,
    fetch_and_cache_image,
    get_image_source,
    image_id_for_url,
    register_image_sources,
    update_image_source_metadata,
)
from .dependencies.auth_dependencies import (
    image_cookie_interceptor,
    token_interceptor,
)

router = APIRouter()

VERSION_URL = "https://raw.githubusercontent.com/plsy1/opendata-insight/main/VERSION"


def _image_headers(cached: CachedImage) -> dict[str, str]:
    headers = {
        "Cache-Control": CACHE_CONTROL,
        "ETag": f'"{cached.content_etag}"',
        "Vary": "Cookie",
    }
    if cached.stale:
        headers["Warning"] = '110 - "Response is stale"'
    return headers


async def _serve_image(request: Request, db: Session, image_id: str):
    source = get_image_source(db, image_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Image not found")

    cached = await fetch_and_cache_image(source)
    update_image_source_metadata(db, source, cached)
    headers = _image_headers(cached)

    request_etags = {
        value.strip() for value in request.headers.get("if-none-match", "").split(",")
    }
    if "*" in request_etags or headers["ETag"] in request_etags:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)

    return FileResponse(
        cached.path,
        media_type=cached.content_type,
        headers=headers,
    )


@router.get("/images/{image_id}")
async def get_image_by_id(
    image_id: str,
    request: Request,
    db: Session = Depends(get_db),
    dep: None = Depends(image_cookie_interceptor),
):
    return await _serve_image(request, db, image_id)


@router.get("/get_image")
async def get_legacy_image(
    request: Request,
    token: str = Query(...),
    db: Session = Depends(get_db),
    dep: None = Depends(image_cookie_interceptor),
):
    try:
        payload = decrypt_payload(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token")

    if payload.exp < int(time.time()):
        raise HTTPException(status_code=403, detail="Token expired")

    register_image_sources([payload.url])
    return await _serve_image(request, db, image_id_for_url(payload.url))


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

@router.get("/version")
async def get_version():
    # Trying to find VERSION file in project root
    version_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "VERSION",
    )
    if os.path.exists(version_path):
        with open(version_path, "r") as f:
            return {"version": f.read().strip()}
    return {"version": "1.0.0-dev"}

@router.get("/check_update")
async def check_update():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(VERSION_URL)
            if response.status_code == 200:
                return {"latest_version": response.text.strip()}
    except Exception as e:
        print(f"Failed to check version: {e}")
    return {"latest_version": None}
