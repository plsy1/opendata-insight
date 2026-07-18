import base64
from datetime import datetime

from database import ActorData, MovieData, MovieSubscribe, ActorSubscribe
from schemas.movies import MovieDataOut, MovieProductOut
from copy import deepcopy
from utils.logs import LOG_ERROR
from services.avbase import get_actor_information_by_name_service
from schemas.feed import (
    MovieFeedItemOut,
    MovieFeedPageOut,
    MovieSubscriptionRulesOut,
    MovieSubscriptionRulesUpdate,
)
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload, Session
from enum import Enum
from dataclasses import dataclass
import re
from services.torrent_metadata import (
    TorrentTitleMetadata,
    normalize_codec,
    normalize_resolution,
    parse_torrent_title_metadata,
)


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


def _normalize_match_keywords(value) -> tuple[str, ...]:
    if not value:
        return ()
    if isinstance(value, str):
        values = re.split(r"[,，;；\n]", value)
    else:
        values = value
    return tuple(
        dict.fromkeys(
            str(keyword).strip().casefold()
            for keyword in values
            if str(keyword).strip()
        )
    )


@dataclass(frozen=True)
class SubscriptionMatchRule:
    resolution: str | None = None
    codec: str | None = None
    required_keywords: tuple[str, ...] = ()
    any_keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    title_regex: str = ""

    @classmethod
    def from_value(cls, value) -> "SubscriptionMatchRule":
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        data = value if isinstance(value, dict) else {}
        resolution = data.get("resolution")
        codec = data.get("codec")
        return cls(
            resolution=normalize_resolution(str(resolution)) if resolution else None,
            codec=normalize_codec(str(codec)) if codec else None,
            required_keywords=_normalize_match_keywords(
                data.get("required_keywords")
            ),
            any_keywords=_normalize_match_keywords(data.get("any_keywords")),
            excluded_keywords=_normalize_match_keywords(
                data.get("excluded_keywords")
            ),
            title_regex=str(data.get("title_regex") or "").strip(),
        )

    def matches(self, title: str, metadata: TorrentTitleMetadata) -> bool:
        normalized_title = title.casefold()
        if any(keyword in normalized_title for keyword in self.excluded_keywords):
            return False
        if any(
            keyword not in normalized_title for keyword in self.required_keywords
        ):
            return False
        if self.any_keywords and not any(
            keyword in normalized_title for keyword in self.any_keywords
        ):
            return False
        if self.title_regex:
            try:
                if re.search(self.title_regex, title, re.IGNORECASE) is None:
                    return False
            except re.error:
                return False
        if self.resolution and metadata.resolution != self.resolution:
            return False
        if self.codec and metadata.codec != self.codec:
            return False
        return True


def subscription_rules_from_values(
    values,
) -> tuple[SubscriptionMatchRule, ...]:
    if not values:
        return ()
    return tuple(SubscriptionMatchRule.from_value(value) for value in values)


def select_best_subscription_resource(
    search_results: list[dict],
    rules: tuple[SubscriptionMatchRule, ...] | None = None,
    global_excluded_keywords=None,
) -> dict | None:
    global_excluded = _normalize_match_keywords(global_excluded_keywords)
    matched = []
    for result in search_results:
        title = str(result.get("title") or "")
        normalized_title = title.casefold()
        if any(keyword in normalized_title for keyword in global_excluded):
            continue
        matched.append(result)
    if not matched:
        return None

    def seeders(result: dict) -> int:
        try:
            return int(result.get("seeders") or 0)
        except (TypeError, ValueError):
            return 0

    if rules:
        parsed_results = [
            (
                result,
                str(result.get("title") or ""),
                parse_torrent_title_metadata(str(result.get("title") or "")),
            )
            for result in matched
        ]
        for rule in rules:
            group_matches = [
                result
                for result, title, metadata in parsed_results
                if rule.matches(title, metadata)
            ]
            if group_matches:
                return max(group_matches, key=seeders)
        return None

    return max(matched, key=seeders)


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
            await get_actor_information_by_name_service(db, name)
            actor = db.query(ActorData).filter(ActorData.name == name).first()
            if actor is None:
                raise RuntimeError(f"Actor data was not persisted for {name}")

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


def _movie_feed_query(db: Session, downloaded: bool):
    return (
        db.query(MovieSubscribe)
        .join(MovieSubscribe.movie)
        .options(
            selectinload(MovieSubscribe.movie).selectinload(MovieData.products),
            selectinload(MovieSubscribe.movie).selectinload(MovieData.subscribers),
        )
        .filter(
            MovieSubscribe.is_downloaded == downloaded,
            MovieData.products.any(),
        )
    )


def _movie_feed_item(sub: MovieSubscribe) -> MovieFeedItemOut:
    movie_out = MovieDataOut.model_validate(sub.movie)
    merged_product = _merge_products(movie_out.products)

    img_url = merged_product.image_url
    if not img_url and merged_product.thumbnail_url:
        img_url = merged_product.thumbnail_url.replace("ps.jpg", "pl.jpg")

    actor_names = {
        actor.get("name")
        for actor in (movie_out.actors + movie_out.casts)
        if actor.get("name")
    }

    movie_out.primary_product = merged_product
    return MovieFeedItemOut(
        id=movie_out.work_id,
        full_id=f"{movie_out.prefix}:{movie_out.work_id}",
        title=merged_product.title or movie_out.title,
        release_date=merged_product.date or movie_out.min_date or "",
        img_url=img_url or "",
        actors=list(actor_names),
        movie=movie_out,
        subscription_rules=_movie_subscription_rules_out(sub.rule_config),
    )


def movie_subscribe_list_service(
    db: Session, status: MovieStatus
) -> list[MovieFeedItemOut]:
    subs = (
        _movie_feed_query(db, status == MovieStatus.DOWNLOADED)
        .order_by(MovieSubscribe.created_at.desc())
        .all()
    )
    return [_movie_feed_item(sub) for sub in subs]


def _encode_download_cursor(sub: MovieSubscribe) -> str:
    value = f"{sub.created_at.isoformat()}|{sub.movie_id}"
    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


def _decode_download_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        value = base64.urlsafe_b64decode(padded.encode()).decode()
        created_at, movie_id = value.rsplit("|", 1)
        return datetime.fromisoformat(created_at), int(movie_id)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid download history cursor") from exc


def movie_downloaded_page_service(
    db: Session,
    *,
    limit: int = 30,
    cursor: str | None = None,
) -> MovieFeedPageOut:
    base_query = _movie_feed_query(db, True)
    total = base_query.count()

    if cursor:
        cursor_created_at, cursor_movie_id = _decode_download_cursor(cursor)
        base_query = base_query.filter(
            or_(
                MovieSubscribe.created_at < cursor_created_at,
                and_(
                    MovieSubscribe.created_at == cursor_created_at,
                    MovieSubscribe.movie_id < cursor_movie_id,
                ),
            )
        )

    rows = (
        base_query.order_by(
            MovieSubscribe.created_at.desc(),
            MovieSubscribe.movie_id.desc(),
        )
        .limit(limit + 1)
        .all()
    )
    has_more = len(rows) > limit
    page_rows = rows[:limit]
    return MovieFeedPageOut(
        items=[_movie_feed_item(sub) for sub in page_rows],
        next_cursor=(
            _encode_download_cursor(page_rows[-1])
            if has_more and page_rows
            else None
        ),
        has_more=has_more,
        total=total,
    )


def _movie_subscription_rules_out(rule_config) -> MovieSubscriptionRulesOut:
    if not isinstance(rule_config, dict):
        return MovieSubscriptionRulesOut(use_global=True)
    return MovieSubscriptionRulesOut(
        use_global=False,
        global_excluded_keywords=rule_config.get(
            "global_excluded_keywords",
            [],
        ),
        quality_rules=rule_config.get("quality_rules", []),
    )


def update_movie_subscription_rules_service(
    db: Session,
    work_id: str,
    rules: MovieSubscriptionRulesUpdate,
) -> bool:
    subscription = (
        db.query(MovieSubscribe)
        .join(MovieData, MovieSubscribe.movie_id == MovieData.id)
        .filter(MovieData.work_id == work_id)
        .first()
    )
    if subscription is None:
        return False

    try:
        subscription.rule_config = (
            None
            if rules.use_global
            else {
                "global_excluded_keywords": rules.global_excluded_keywords,
                "quality_rules": [
                    rule.model_dump() for rule in rules.quality_rules
                ],
            }
        )
        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        LOG_ERROR(exc)
        return False


def actor_list_service(
    db: Session,
    list_type: ActorListType,
) -> list[ActorData]:
    if list_type == ActorListType.SUBSCRIBE:
        condition = ActorSubscribe.is_subscribe.is_(True)
        order_by = ActorSubscribe.subscribe_order.desc()
    elif list_type == ActorListType.COLLECT:
        condition = ActorSubscribe.is_collect.is_(True)
        order_by = ActorSubscribe.collect_order.desc()
    else:
        raise ValueError("Invalid ActorListType")

    actors = (
        db.query(ActorData)
        .join(ActorSubscribe)
        .filter(condition)
        .order_by(order_by, ActorSubscribe.created_at.desc())
        .all()
    )

    return actors


def update_actor_order_service(
    db: Session,
    list_type: ActorListType,
    names: list[str],
) -> bool:
    try:
        # We assign descending order based on the list position:
        # The first item gets the highest order value.
        count = len(names)
        for index, name in enumerate(names):
            actor = db.query(ActorData).filter(ActorData.name == name).first()
            if actor and actor.subscribers:
                order_value = count - index
                if list_type == ActorListType.SUBSCRIBE:
                    actor.subscribers.subscribe_order = order_value
                else:
                    actor.subscribers.collect_order = order_value
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        LOG_ERROR(e)
        return False


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


def _merge_products(products: list[MovieProductOut]) -> MovieProductOut:
    if not products:
        return None

    merged = deepcopy(products[0])

    for prod in products[1:]:
        for field, value in prod.model_dump().items():
            current_value = getattr(merged, field)

            if isinstance(value, list):
                value = value or []
                current_value = current_value or []
                merged_list = current_value + [
                    v for v in value if v not in current_value
                ]
                setattr(merged, field, merged_list)
            else:
                if (current_value is None or current_value == "") and value not in (
                    None,
                    "",
                ):
                    setattr(merged, field, value)

    return merged
