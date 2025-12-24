from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from modules.metadata.fanza.model import RankingType


router = APIRouter()


@router.get("/monthlyactress")
async def fetch_actress_ranking(
    page: int = 1, isValid: str = Depends(tokenInterceptor)
):
    from modules.metadata.fanza import fetch_actress_ranking

    actresses = await fetch_actress_ranking(page)
    return actresses


@router.get("/monthlyworks")
async def fetch_dvd_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
    isValid: str = Depends(tokenInterceptor),
):
    from modules.metadata.fanza import fetch_movie_ranking

    works = await fetch_movie_ranking(page, term)
    return works
