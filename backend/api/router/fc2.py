from fastapi import APIRouter, Depends
from core.auth import tokenInterceptor
from modules.metadata.fc2.model import RankingType
from core.database import FC2Metadata, get_db
from modules.metadata.fc2 import get_ranking
from datetime import datetime

router = APIRouter()


@router.get("/detials/{number}")
async def fetch_details(
    number: str,
):
    from modules.metadata.fc2 import get_information_by_number

    return await get_information_by_number(number)


@router.get("/ranking")
async def fetch_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
):
    db = next(get_db())

    try:
        records = (
            db.query(FC2Metadata)
            .filter(
                FC2Metadata.term == term.value,
                FC2Metadata.page == page,
            )
            .order_by(FC2Metadata.rank.asc())
            .all()
        )

        if records:
            return records

        items = await get_ranking(page=page, term=term)
        if not items:
            return []

        for item in items:
            db.add(
                FC2Metadata(
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
            db.query(FC2Metadata)
            .filter(
                FC2Metadata.term == term.value,
                FC2Metadata.page == page,
            )
            .order_by(FC2Metadata.rank.asc())
            .all()
        )

        return records

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
