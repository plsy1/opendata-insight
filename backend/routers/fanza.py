from fastapi import APIRouter, HTTPException, status
from modules.metadata.fanza.model import Actress, RankingType, Work
from modules.metadata.fanza import *
from services.system import replace_domain_in_value

router = APIRouter()


@router.get("/monthlyactress", response_model=list[Actress])
async def fetch_actress(page: int = 1):
    try:
        result = await fetch_actress_ranking(page)
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}"
        )


@router.get("/monthlyworks", response_model=list[Work])
async def fetch_dvd_ranking(page: int = 1, term: RankingType = RankingType.monthly):
    try:
        result = await fetch_movie_ranking(page, term)
        return replace_domain_in_value(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed: {e}"
        )
