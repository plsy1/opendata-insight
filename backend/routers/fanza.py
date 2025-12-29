from fastapi import APIRouter, Depends, HTTPException
from services.auth import tokenInterceptor
from modules.metadata.fanza.model import RankingType
from modules.metadata.fanza import *
from services.system import replace_domain_in_value

router = APIRouter()


@router.get("/monthlyactress")
async def fetch_actress(
    page: int = 1, isValid: str = Depends(tokenInterceptor)
):
    try:
        result = await fetch_actress_ranking(page)
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")


@router.get("/monthlyworks")
async def fetch_dvd_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
    isValid: str = Depends(tokenInterceptor),
):
    try:
        result = await fetch_movie_ranking(page, term)
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {e}")
