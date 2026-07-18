from fastapi import APIRouter, HTTPException, Path, Query, Depends
from database import get_db
from modules.metadata.fc2.model import RankingType
from services.fc2 import get_fc2_details, get_fc2_ranking, get_fc2_seller
from services.system import replace_domain_in_value
from sqlalchemy.orm import Session
from schemas.fc2 import FC2ProductOut, FC2RankingOut, FC2SellerWorksOut

router = APIRouter()


@router.get("/details", response_model=FC2ProductOut)
async def fetch_details(number: str, db: Session = Depends(get_db)):
    try:
        product = await get_fc2_details(number, db)
        payload = FC2ProductOut.model_validate(product).model_dump()
        return replace_domain_in_value(payload)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch details: {e}")
    finally:
        db.close()


@router.get("/ranking", response_model=list[FC2RankingOut])
async def fetch_ranking(
    page: int = Query(1, ge=1, le=5),
    term: RankingType = RankingType.monthly,
    db: Session = Depends(get_db),
):
    try:
        records = await get_fc2_ranking(page, term, db)
        payload = [
            FC2RankingOut.model_validate(record).model_dump()
            for record in records
        ]
        return replace_domain_in_value(payload)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to fetch ranking: {e}")
    finally:
        db.close()


@router.get("/sellers/{seller_id}", response_model=FC2SellerWorksOut)
async def fetch_seller(
    seller_id: str = Path(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    try:
        result = await get_fc2_seller(seller_id, page, db)
        payload = FC2SellerWorksOut.model_validate(result).model_dump()
        return replace_domain_in_value(payload)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch FC2 seller: {e}",
        )
    finally:
        db.close()
