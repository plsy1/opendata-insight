from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import FC2Product, FC2Ranking, FC2Seller
from modules.metadata.fc2 import (
    get_information_by_number,
    get_ranking,
    get_seller_information as fetch_seller_information,
    get_seller_works as fetch_seller_works,
)
from modules.metadata.fc2.model import FC2SellerInformation, RankingType


SELLER_PROFILE_TTL = timedelta(days=1)


def _seller_metadata(seller: FC2Seller) -> FC2SellerInformation:
    return FC2SellerInformation(
        seller_id=seller.seller_id,
        author_id=seller.author_id,
        name=seller.name,
        profile_url=seller.profile_url,
        avatar_url=seller.avatar_url,
        banner_url=seller.banner_url,
        short_intro=seller.short_intro,
        description=seller.description,
        product_count=seller.product_count or 0,
        follower_count=seller.follower_count or 0,
    )


def _save_seller(info: FC2SellerInformation, db: Session) -> FC2Seller:
    seller = (
        db.query(FC2Seller)
        .filter(FC2Seller.seller_id == info.seller_id)
        .first()
    )
    if not seller:
        seller = FC2Seller(seller_id=info.seller_id)
        db.add(seller)

    seller.author_id = info.author_id
    seller.name = info.name
    seller.profile_url = info.profile_url
    seller.avatar_url = info.avatar_url
    seller.banner_url = info.banner_url
    seller.short_intro = info.short_intro
    seller.description = info.description
    seller.product_count = info.product_count
    seller.follower_count = info.follower_count
    seller.crawled_at = datetime.now()
    db.flush()
    return seller


async def _get_seller_profile(seller_id: str, db: Session) -> FC2Seller:
    seller = (
        db.query(FC2Seller)
        .filter(FC2Seller.seller_id == seller_id)
        .first()
    )
    is_fresh = bool(
        seller
        and seller.crawled_at
        and datetime.now() - seller.crawled_at < SELLER_PROFILE_TTL
    )
    if is_fresh:
        return seller

    try:
        info = await fetch_seller_information(seller_id)
    except Exception:
        if seller:
            return seller
        raise

    seller = _save_seller(info, db)
    db.commit()
    db.refresh(seller)
    return seller


async def get_fc2_details(number: str, db: Session):
    product = db.query(FC2Product).filter(FC2Product.article_id == number).first()

    # Old caches did not capture the seller link. Refresh them once on access.
    if product and product.seller_id and product.product_id:
        return product

    try:
        info = await get_information_by_number(number)
    except Exception:
        if product:
            return product
        raise

    if not info:
        raise HTTPException(status_code=404, detail="No details found.")

    if not product:
        product = FC2Product(article_id=number)
        db.add(product)

    product.product_id = info.product_id
    product.title = info.title
    product.author = info.author
    product.seller_id = info.seller_id
    product.cover = info.cover
    product.duration = info.duration
    product.sale_day = info.sale_day
    product.sample_images = info.sample_images
    product.crawled_at = datetime.now()

    db.commit()
    db.refresh(product)
    return product


async def get_fc2_seller(seller_id: str, page: int, db: Session):
    seller = await _get_seller_profile(seller_id, db)
    cached_works = (
        db.query(FC2Product)
        .filter(
            FC2Product.seller_id == seller_id,
            FC2Product.seller_page == page,
        )
        .order_by(FC2Product.seller_position.asc())
        .all()
    )

    try:
        result = await fetch_seller_works(_seller_metadata(seller), page)
    except Exception:
        if cached_works:
            return {
                "seller": seller,
                "works": cached_works,
                "page": page,
                "total": seller.product_count or len(cached_works),
                "has_next": page * 30 < (seller.product_count or 0),
            }
        raise

    current_ids = {work.article_id for work in result.works}
    for cached in cached_works:
        if cached.article_id not in current_ids:
            cached.seller_page = None
            cached.seller_position = None

    saved_works: list[FC2Product] = []
    for position, work in enumerate(result.works, start=1):
        product = (
            db.query(FC2Product)
            .filter(FC2Product.article_id == work.article_id)
            .first()
        )
        if not product:
            product = FC2Product(article_id=work.article_id, sample_images=[])
            db.add(product)

        product.title = work.title
        product.author = work.seller_name or seller.name
        product.seller_id = seller_id
        product.cover = work.cover
        product.duration = work.duration
        product.description = work.description
        product.price = work.price
        product.rating = work.rating
        product.comment_count = work.comment_count
        product.favorite_count = work.favorite_count
        product.seller_page = page
        product.seller_position = position
        product.crawled_at = datetime.now()
        saved_works.append(product)

    if result.total and seller.product_count != result.total:
        seller.product_count = result.total
    db.commit()

    for product in saved_works:
        db.refresh(product)
    db.refresh(seller)
    return {
        "seller": seller,
        "works": saved_works,
        "page": result.page,
        "total": result.total,
        "has_next": result.has_next,
    }


async def get_fc2_ranking(page: int, term: RankingType, db: Session):
    records = (
        db.query(FC2Ranking)
        .filter(
            FC2Ranking.term == term.value,
            FC2Ranking.page == page,
        )
        .order_by(FC2Ranking.rank.asc())
        .all()
    )

    if records and all(record.seller_id and record.owner for record in records):
        return records

    items = await get_ranking(page=page, term=term)
    if not items:
        return records

    existing = {
        (record.article_id, record.rank): record
        for record in records
    }
    for item in items:
        record = existing.get((item.article_id, item.rank))
        if not record:
            record = FC2Ranking(
                term=term.value,
                article_id=item.article_id,
                page=page,
                rank=item.rank,
            )
            db.add(record)

        record.title = item.title
        record.url = str(item.url)
        record.cover = str(item.cover) if item.cover else None
        record.owner = item.owner
        record.seller_id = item.seller_id
        record.rating = item.rating
        record.comment_count = item.comment_count
        record.hot_comments = item.hot_comments
        record.is_active = True
        record.crawled_at = datetime.now()

    db.commit()

    return (
        db.query(FC2Ranking)
        .filter(
            FC2Ranking.term == term.value,
            FC2Ranking.page == page,
        )
        .order_by(FC2Ranking.rank.asc())
        .all()
    )
