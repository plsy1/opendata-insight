from fastapi import APIRouter, HTTPException, Query, Depends
from database import get_db
from modules.metadata.fc2.model import RankingType
from services.fc2 import get_fc2_details, get_fc2_ranking
from services.system import replace_domain_in_value
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/details")
async def fetch_details(number: str, db: Session = Depends(get_db)):
    try:
        product = await get_fc2_details(number, db)
        return replace_domain_in_value(product)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch details: {e}")
    finally:
        db.close()


@router.get("/ranking")
async def fetch_ranking(
    page: int = Query(1, ge=1, le=5),
    term: RankingType = RankingType.monthly,
    db: Session = Depends(get_db),
):
    try:
        records = await get_fc2_ranking(page, term, db)
        return replace_domain_in_value(records)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch ranking: {e}")
    finally:
        db.close()
