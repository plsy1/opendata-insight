import re
from copy import deepcopy
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from database import MovieData
from schemas.movies import MovieDataOut, MovieProductOut


WORK_ID_TAG_PREFIX = "avbase-work:"
FC2_ID_TAG_PREFIX = "fc2-work:"
_SEPARATED_WORK_ID = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]{1,24}[-_]\d{2,8})(?![A-Za-z0-9])"
)
_COMPACT_WORK_ID = re.compile(r"(?<![A-Za-z])([A-Za-z]{2,16})(0*\d{2,8})(?!\d)")
_MEDIA_SUFFIX = re.compile(r"\.(?:torrent|mkv|mp4|avi|wmv|mov|ts)$", re.IGNORECASE)


def _canonical_work_id(work_id: str) -> str:
    value = work_id.strip()
    return value.split(":", 1)[1] if ":" in value else value


def resolve_download_media_type(
    media_type: str | None,
    work_id: str | None = None,
) -> str | None:
    requested_type = str(media_type or "").strip().casefold()
    if requested_type in {"jav", "fc2"}:
        return requested_type

    canonical_work_id = _canonical_work_id(work_id or "")
    if not canonical_work_id:
        return None
    if canonical_work_id.casefold().startswith("fc2") or canonical_work_id.isdigit():
        return "fc2"
    return "jav"


def build_download_tags(
    base_tag: str,
    work_id: str | None,
    media_type: str | None = None,
) -> str:
    tags = [tag.strip() for tag in base_tag.split(",") if tag.strip()]
    canonical_work_id = _canonical_work_id(work_id or "")
    if canonical_work_id:
        prefix = (
            FC2_ID_TAG_PREFIX
            if resolve_download_media_type(media_type, canonical_work_id) == "fc2"
            else WORK_ID_TAG_PREFIX
        )
        tags.append(f"{prefix}{canonical_work_id}")
    return ",".join(dict.fromkeys(tags))


def _candidate_work_ids(torrent: dict[str, Any]) -> list[str]:
    candidates: list[str] = []

    for tag in str(torrent.get("tags") or "").split(","):
        tag = tag.strip()
        if tag.lower().startswith(WORK_ID_TAG_PREFIX):
            candidates.append(tag[len(WORK_ID_TAG_PREFIX) :].strip())

    name = str(torrent.get("name") or "").strip()
    basename = name.replace("\\", "/").rsplit("/", 1)[-1]
    basename = _MEDIA_SUFFIX.sub("", basename).strip()
    if basename:
        candidates.append(basename)

    for match in _SEPARATED_WORK_ID.finditer(name):
        candidate = match.group(1).replace("_", "-")
        candidates.append(candidate)
        prefix, digits = candidate.rsplit("-", 1)
        stripped_digits = digits.lstrip("0") or "0"
        candidates.append(f"{prefix}-{stripped_digits}")

    for match in _COMPACT_WORK_ID.finditer(name):
        prefix, digits = match.groups()
        candidates.append(f"{prefix}-{digits}")
        candidates.append(f"{prefix}-{digits.lstrip('0') or '0'}")

    unique_candidates: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.casefold()
        if candidate and key not in seen:
            seen.add(key)
            unique_candidates.append(candidate)
    return unique_candidates


def _merge_products(products: list[MovieProductOut]) -> MovieProductOut | None:
    if not products:
        return None

    merged = deepcopy(products[0])
    for product in products[1:]:
        for field, value in product.model_dump().items():
            current_value = getattr(merged, field)
            if isinstance(value, list):
                current_items = current_value or []
                setattr(
                    merged,
                    field,
                    current_items
                    + [item for item in (value or []) if item not in current_items],
                )
            elif (current_value is None or current_value == "") and value not in (
                None,
                "",
            ):
                setattr(merged, field, value)

    if not merged.image_url and merged.thumbnail_url:
        merged.image_url = merged.thumbnail_url.replace("ps.jpg", "pl.jpg")
    return merged


def _movie_out(movie: MovieData) -> MovieDataOut:
    result = MovieDataOut.model_validate(movie)
    result.primary_product = _merge_products(result.products)
    return result


def enrich_downloading_torrents(
    db: Session,
    torrents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach complete movie metadata to qBittorrent tasks in one database query."""
    candidate_lists = [_candidate_work_ids(torrent) for torrent in torrents]
    candidate_keys = {
        candidate.casefold()
        for candidates in candidate_lists
        for candidate in candidates
    }

    movies_by_work_id: dict[str, MovieDataOut] = {}
    if candidate_keys:
        movies = (
            db.query(MovieData)
            .options(
                selectinload(MovieData.products),
                selectinload(MovieData.subscribers),
            )
            .filter(func.lower(MovieData.work_id).in_(candidate_keys))
            .all()
        )
        movies_by_work_id = {
            movie.work_id.casefold(): _movie_out(movie) for movie in movies
        }

    results: list[dict[str, Any]] = []
    for torrent, candidates in zip(torrents, candidate_lists):
        item = dict(torrent)
        movie = next(
            (
                movies_by_work_id[candidate.casefold()]
                for candidate in candidates
                if candidate.casefold() in movies_by_work_id
            ),
            None,
        )
        item["work_id"] = movie.work_id if movie else None
        item["movie"] = movie
        results.append(item)

    return results
