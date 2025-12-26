from core.database import RSSItem, ActorData, get_db
from core.logs import LOG_ERROR
from modules.metadata.avbase import *
from modules.notification.telegram.text import *
from .model import *
from core.config import _config


async def actor_operation_service(
    name: str,
    operation: Operation,
) -> bool:
    db = next(get_db())
    try:
        record = db.query(ActorData).filter(ActorData.name == name).first()

        if operation in (Operation.UNSUBSCRIBE, Operation.UNCOLLECT):
            if not record:
                return True
            if operation == Operation.UNSUBSCRIBE:
                record.isSubscribe = False
            else:
                record.isCollect = False

            db.commit()
            return True

        if record:
            if operation == Operation.SUBSCRIBE:
                record.isSubscribe = True
            elif operation == Operation.COLLECT:
                record.isCollect = True

            db.commit()
            db.refresh(record)
            data = ActorDataResponse.model_validate(record)

        else:
            data = await get_actress_info_by_actress_name(name)

            new_actor = ActorData(
                **data.model_dump(),
                isSubscribe=(operation == Operation.SUBSCRIBE),
                isCollect=(operation == Operation.COLLECT),
            )
            db.add(new_actor)
            db.commit()
            db.refresh(new_actor)

            data = ActorDataResponse.model_validate(new_actor)

        if operation == Operation.SUBSCRIBE:
            actress_details = actressInformation(data)
            from modules.notification.telegram import _telegram_bot

            await _telegram_bot.send_message_with_image(
                data.avatar_url,
                actress_details,
            )

        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


def movie_subscribe_list_service(type: MovieStatus, changeImagePrefix: bool = False):
    db = next(get_db())
    downloaded_flag = type == MovieStatus.DOWNLOADED

    feeds = (
        db.query(RSSItem)
        .filter(RSSItem.downloaded == downloaded_flag)
        .order_by(RSSItem.id.desc())
        .all()
    )

    if changeImagePrefix:
        feeds = replace_domain_in_value(
            feeds,
            _config.get("SYSTEM_IMAGE_PREFIX"),
        )

    return feeds


def actor_list_service(list_type: ActorListType, changeImagePrefix: bool = False):

    db = next(get_db())

    if list_type == ActorListType.SUBSCRIBE:
        condition = ActorData.isSubscribe.is_(True)
    elif list_type == ActorListType.COLLECT:
        condition = ActorData.isCollect.is_(True)
    else:
        raise ValueError("Invalid ActorListType")

    actors = db.query(ActorData).filter(condition).all()

    if changeImagePrefix:
        actors = replace_domain_in_value(
            actors,
            _config.get("SYSTEM_IMAGE_PREFIX"),
        )

    return actors


async def movie_feed_service(
    operation: MovieFeedOperation,
    *,
    keyword: str,
    actors: str | None = None,
    img: str | None = None,
    link: str | None = None,
) -> bool:
    from modules.notification.telegram import _telegram_bot

    db = next(get_db())

    try:
        if operation == MovieFeedOperation.REMOVE:
            feed = db.query(RSSItem).filter(RSSItem.keyword == keyword).first()
            if not feed:
                return True

            db.delete(feed)
            db.commit()
            return True

        feed = db.query(RSSItem).filter(RSSItem.keyword == keyword).first()

        if feed:
            feed.downloaded = False
        else:
            feed = RSSItem(
                actors=actors,
                keyword=keyword,
                img=img,
                link=link,
                downloaded=False,
            )
            db.add(feed)

        db.commit()
        db.refresh(feed)

        movie_info = await get_information_by_work_id(link)
        movie_details = movieInformation(keyword, movie_info)

        img_url = str(movie_info.products[0].image_url)
        await _telegram_bot.send_message_with_image(
            img_url,
            movie_details,
        )

        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False
