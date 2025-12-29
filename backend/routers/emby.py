from fastapi import APIRouter, Depends, HTTPException
from services.auth import tokenInterceptor
from database import get_db, EmbyMovie
from sqlalchemy.orm import Session
from backend.utils.extract_code import extract_jav_code

router = APIRouter()


@router.get("/get_item_counts")
async def get_item_counts(isValid: str = Depends(tokenInterceptor)):
    from modules.mediaServer.emby import _emby_instance

    try:
        results = _emby_instance.request("/Items/Counts", use_header=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/get_resume")
async def get_resume(isValid: str = Depends(tokenInterceptor)):
    from modules.mediaServer.emby import _emby_instance

    try:
        return _emby_instance.get_resume_items()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/get_latest")
async def get_latest(isValid: str = Depends(tokenInterceptor)):
    from modules.mediaServer.emby import _emby_instance

    try:
        return _emby_instance.get_latest_items()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/get_views")
async def get_latest(isValid: str = Depends(tokenInterceptor)):
    from modules.mediaServer.emby import _emby_instance

    try:
        return _emby_instance.get_views()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/get_all")
async def get_latest(isValid: str = Depends(tokenInterceptor)):
    from modules.mediaServer.emby import _emby_instance

    try:
        return _emby_instance.get_all_movies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/exists")
async def exists(
    title: str, db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        jav_code = extract_jav_code(title)
        movie = (
            db.query(EmbyMovie).filter(EmbyMovie.name.ilike(f"%{jav_code}%")).first()
        )
        exists_flag, index_link = (True, movie.indexLink) if movie else (False, None)

        return {"exists": exists_flag, "indexLink": index_link}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")
