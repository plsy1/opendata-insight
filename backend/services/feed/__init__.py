from core.database import RSSItem, RSSFeed, ActorData, ActressCollect, get_db
from core.logs import LOG_ERROR
from modules.metadata.avbase import *
from modules.notification.telegram.text import *
from sqlalchemy.orm import Session


async def add_movie_feed(
    actors: str, keyword: str, img: str, link: str, db: Session
) -> bool:
    from modules.notification.telegram import _telegram_bot

    try:
        feed = db.query(RSSItem).filter(RSSItem.keyword == keyword).first()
        if feed:
            feed.downloaded = False
        else:
            feed = RSSItem(
                actors=actors, keyword=keyword, img=img, link=link, downloaded=False
            )
            db.add(feed)

        db.commit()
        db.refresh(feed)

        movie_info = await get_information_by_work_id(link)
        movie_details = movieInformation(keyword, movie_info)

        imgURL = str(movie_info.products[0].image_url)
        await _telegram_bot.send_message_with_image(imgURL, movie_details)

        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


async def remove_movie_feed(
    keyword: str,
    db: Session,
):
    existing_keyword = db.query(RSSItem).filter(RSSItem.keyword == keyword).first()

    if not existing_keyword:
        raise HTTPException(status_code=404, detail="Keyword not found.")

    try:
        db.delete(existing_keyword)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


async def add_performer_feed(
    actor_name: str,
    db: Session,
):

    try:


        record = db.query(ActorData).filter(ActorData.name == actor_name).first()
        if record:
            record.isSubscribe = 1
            db.commit()
            db.refresh(record)

            data = Actress.model_validate(record)

        else:
            data = await get_actress_info_by_actress_name(actor_name)

            new_actor = ActorData(
                **data.dict(exclude={"raw_avatar_url"}),
                isSubscribe=True,
                isCollect=False,
            )
            db.add(new_actor)
            db.commit()
            db.refresh(new_actor)

        actress_details = actressInformation(data)
        from modules.notification.telegram import _telegram_bot

        await _telegram_bot.send_message_with_image(data.avatar_url, actress_details)
        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False
