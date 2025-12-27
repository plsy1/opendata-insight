from database import ActorData, MovieData, MovieSubscribe, ActorSubscribe
from utils.logs import LOG_ERROR
from modules.metadata.avbase import *
from modules.notification.telegram.text import *
from .model import *
from config import _config
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session
from schemas.actor import ActorDataOut

async def actor_operation_service(
    db: Session,
    name: str,
    operation: Operation,
) -> bool:
    try:
        actor = db.query(ActorData).filter(ActorData.name == name).first()

        if operation in (Operation.UNSUBSCRIBE, Operation.UNCOLLECT):
            if not actor or not actor.subscribers:
                return True

            if operation == Operation.UNSUBSCRIBE:
                actor.subscribers.is_subscribe = False
            else:
                actor.subscribers.is_collect = False

            db.commit()
            return True

        if not actor:
            data = await get_actress_info_by_actress_name(name)

            actor = ActorData(**data.model_dump())
            db.add(actor)
            db.flush()

        if not actor.subscribers:
            actor.subscribers = ActorSubscribe(
                is_subscribe=(operation == Operation.SUBSCRIBE),
                is_collect=(operation == Operation.COLLECT),
            )
        else:
            if operation == Operation.SUBSCRIBE:
                actor.subscribers.is_subscribe = True
            elif operation == Operation.COLLECT:
                actor.subscribers.is_collect = True

        db.commit()
        db.refresh(actor)

        if operation == Operation.SUBSCRIBE:
            actress_details = actressInformation(
                ActorDataOut.model_validate(actor)
            )
            from modules.notification.telegram import _telegram_bot

            await _telegram_bot.send_message_with_image(
                actor.avatar_url,
                actress_details,
            )

        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


def movie_subscribe_list_service(
    db: Session,
    status: MovieStatus,
    changeImagePrefix: bool = False,
):

    downloaded_flag = status == MovieStatus.DOWNLOADED

    subs = (
        db.query(MovieSubscribe)
        .options(selectinload(MovieSubscribe.movie).selectinload(MovieData.products))
        .filter(MovieSubscribe.is_downloaded == downloaded_flag)
        .order_by(MovieSubscribe.created_at.desc())
        .all()
    )

    result: list[MovieDataOut] = []

    for sub in subs:
        movie = sub.movie

        movie_out = MovieDataOut.model_validate(movie)

        result.append(movie_out)

    if changeImagePrefix:
        result = replace_domain_in_value(
            result,
            _config.get("SYSTEM_IMAGE_PREFIX"),
        )

    return result


def actor_list_service(
    db: Session,
    list_type: ActorListType,
    changeImagePrefix: bool = False,
) -> list[ActorData]:
    if list_type == ActorListType.SUBSCRIBE:
        condition = ActorSubscribe.is_subscribe.is_(True)
    elif list_type == ActorListType.COLLECT:
        condition = ActorSubscribe.is_collect.is_(True)
    else:
        raise ValueError("Invalid ActorListType")

    actors = db.query(ActorData).join(ActorSubscribe).filter(condition).all()

    if changeImagePrefix:
        actors = replace_domain_in_value(
            actors,
            _config.get("SYSTEM_IMAGE_PREFIX"),
        )

    return actors


async def movie_subscribe_service(
    db: Session,
    operation: MovieFeedOperation,
    work_id: str,
) -> bool:
    movie = db.query(MovieData).filter(MovieData.work_id == work_id).first()

    if not movie:
        return False

    try:
        if operation == MovieFeedOperation.REMOVE:
            return _remove_movie_subscribe(db, movie)

        if operation == MovieFeedOperation.ADD:
            return await _add_movie_subscribe(db, movie)

        if operation == MovieFeedOperation.MARK_DOWNLOADED:
            return _mark_movie_downloaded(db, movie)

        return False

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


def _remove_movie_subscribe(db: Session, movie: MovieData) -> bool:
    if not movie.subscribers:
        return True

    db.delete(movie.subscribers)
    db.commit()
    return True


async def _add_movie_subscribe(db: Session, movie: MovieData) -> bool:
    from modules.notification.telegram import _telegram_bot

    if movie.subscribers:
        movie.subscribers.is_downloaded = False
        db.commit()
        return True

    movie.subscribers = MovieSubscribe(is_downloaded=False)
    db.commit()

    movie_info = await get_information_by_work_id(movie.work_id)
    movie_details = movieInformation(movie.title, movie_info)

    img_url = str(movie_info.products[0].image_url)
    await _telegram_bot.send_message_with_image(
        img_url,
        movie_details,
    )

    return True


def _mark_movie_downloaded(db: Session, movie: MovieData) -> bool:
    if not movie.subscribers:
        return False

    movie.subscribers.is_downloaded = True
    db.commit()
    return True
