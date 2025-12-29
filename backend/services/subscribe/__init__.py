from database import ActorData, MovieData, MovieSubscribe, ActorSubscribe
from schemas.movies import MovieDataOut
from utils.logs import LOG_ERROR
from services.avbase import get_actor_information_by_name_service
from sqlalchemy.orm import selectinload, Session
from enum import Enum

class Operation(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    COLLECT = "collect"
    UNCOLLECT = "uncollect"


class MovieStatus(str, Enum):
    SUBSCRIBE = "subscribe"
    DOWNLOADED = "downloaded"


class ActorListType(str, Enum):
    SUBSCRIBE = "subscribe"
    COLLECT = "collect"


class MovieFeedOperation(Enum):
    ADD = "add"
    REMOVE = "remove"
    MARK_DOWNLOADED = "done"


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
            data = await get_actor_information_by_name_service(db, name)

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

        return True

    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


def movie_subscribe_list_service(
    db: Session,
    status: MovieStatus
) -> list[MovieDataOut]:

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

    return result


def actor_list_service(
    db: Session,
    list_type: ActorListType,
) -> list[ActorData]:
    if list_type == ActorListType.SUBSCRIBE:
        condition = ActorSubscribe.is_subscribe.is_(True)
    elif list_type == ActorListType.COLLECT:
        condition = ActorSubscribe.is_collect.is_(True)
    else:
        raise ValueError("Invalid ActorListType")

    actors = db.query(ActorData).join(ActorSubscribe).filter(condition).all()

    return actors


def movie_subscribe_service(
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
            return _add_movie_subscribe(db, movie)

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


def _add_movie_subscribe(db: Session, movie: MovieData) -> bool:
    try:
        if movie.subscribers:
            movie.subscribers.is_downloaded = False
        else:
            movie.subscribers = MovieSubscribe(is_downloaded=False)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


def _mark_movie_downloaded(db: Session, movie: MovieData) -> bool:
    if not movie.subscribers:
        movie.subscribers = MovieSubscribe(is_downloaded=True)
    else:
        movie.subscribers.is_downloaded = True

    db.commit()
    return True
