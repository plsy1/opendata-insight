from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from modules.metadata.fc2.model import RankingType


router = APIRouter()


@router.get("/ranking")
async def fetch_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
):
    from modules.metadata.fc2 import get_ranking

    ranking = await get_ranking(page, term)
    return ranking


@router.get("/detials/{number}")
async def fetch_details(
    number: str,
):
    from modules.metadata.fc2 import get_information_by_number

    return await get_information_by_number(number)
