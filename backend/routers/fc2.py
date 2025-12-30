from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from database import FC2Ranking, FC2Product, get_db
from modules.metadata.fc2 import get_ranking, get_information_by_number
from modules.metadata.fc2.model import RankingType
from services.system import replace_domain_in_value
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/details")
async def fetch_details(number: str, db: Session = Depends(get_db)):

    try:
        product = db.query(FC2Product).filter(FC2Product.article_id == number).first()

        if product:
            return replace_domain_in_value(product)

        info = await get_information_by_number(number)

        if not info:
            raise HTTPException(status_code=404, detail="No details found.")

        info.article_id = number

        stmt = sqlite_insert(FC2Product).values(
            article_id=info.article_id,
            product_id=info.product_id,
            title=info.title,
            author=info.author,
            cover=info.cover,
            duration=info.duration,
            sale_day=info.sale_day,
            sample_images=info.sample_images,
            crawled_at=datetime.now(),
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["article_id", "product_id"],
            set_={
                "title": stmt.excluded.title,
                "author": stmt.excluded.author,
                "cover": stmt.excluded.cover,
                "duration": stmt.excluded.duration,
                "sale_day": stmt.excluded.sale_day,
                "sample_images": stmt.excluded.sample_images,
                "crawled_at": stmt.excluded.crawled_at,
            },
        )

        db.execute(stmt)
        db.commit()

        product = db.query(FC2Product).filter(FC2Product.article_id == number).first()

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
        records = (
            db.query(FC2Ranking)
            .filter(
                FC2Ranking.term == term.value,
                FC2Ranking.page == page,
            )
            .order_by(FC2Ranking.rank.asc())
            .all()
        )

        if records:
            return replace_domain_in_value(records)

        items = await get_ranking(page=page, term=term)
        if not items:
            return []

        for item in items:
            db.add(
                FC2Ranking(
                    term=term.value,
                    article_id=item.article_id,
                    page=page,
                    rank=item.rank,
                    title=item.title,
                    url=str(item.url),
                    cover=str(item.cover) if item.cover else None,
                    owner=item.owner,
                    rating=item.rating,
                    comment_count=item.comment_count,
                    hot_comments=item.hot_comments,
                    crawled_at=datetime.now(),
                )
            )

        db.commit()

        records = (
            db.query(FC2Ranking)
            .filter(
                FC2Ranking.term == term.value,
                FC2Ranking.page == page,
            )
            .order_by(FC2Ranking.rank.asc())
            .all()
        )

        return replace_domain_in_value(records)

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
