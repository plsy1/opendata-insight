import httpx, re
from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from enum import Enum
from core.config import _config
from core.system import replace_domain_in_value

from modules.metadata.fc2 import get_ranking


class RankingType(Enum):
    realtime = "realtime"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    annual = "annual"


router = APIRouter()


@router.get("/ranking")
async def fetch_dvd_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
):
    ranking = await get_ranking(page, term)
    return ranking


@router.get("/detials/{number}")
async def fetch_details(
    number: str,
):
    from modules.metadata.fc2 import get_information_by_number

    return await get_information_by_number(number)
