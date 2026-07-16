import asyncio
import base64
import hashlib
import json
import mimetypes
import os
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import aiofiles
import httpx
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException, status
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from config import _config
from database import ImageSource, SessionLocal
from services.system.model import DecryptedImagePayload


BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / _config.get("CACHE_DIR")
CACHE_EXPIRE_HOURS = int(_config.get("IMAGE_CACHE_HOURS"))
CACHE_CONTROL = f"private, max-age={CACHE_EXPIRE_HOURS * 3600}"
IMAGE_MAX_BYTES = int(_config.get("IMAGE_MAX_BYTES"))

CACHE_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".avif",
)

IMAGE_KEYS = (
    "image",
    "images",
    "img",
    "cover",
    "poster",
    "avatar",
    "thumb",
    "primary",
)

IMAGE_PATH_KEYWORDS = (
    "/images/",
    "/image/",
    "/art/",
    "/poster",
    "/thumb",
    "/backdrop",
    "/primary",
    "/logo",
)


@dataclass
class CachedImage:
    path: Path
    content_type: str
    content_etag: str
    upstream_etag: str | None = None
    upstream_last_modified: str | None = None
    stale: bool = False


@dataclass
class _LockState:
    lock: asyncio.Lock
    users: int = 0


_image_http_client: httpx.AsyncClient | None = None
_image_client_lock = asyncio.Lock()
_image_fetch_semaphore = asyncio.Semaphore(
    int(_config.get("IMAGE_MAX_CONCURRENCY"))
)
_image_locks: dict[str, _LockState] = {}
_image_locks_guard = asyncio.Lock()
_image_runtime_metadata: dict[str, CachedImage] = {}


async def init_image_proxy() -> None:
    global _image_http_client
    async with _image_client_lock:
        if _image_http_client is None:
            _image_http_client = httpx.AsyncClient(
                timeout=float(_config.get("IMAGE_HTTP_TIMEOUT_SECONDS")),
                follow_redirects=True,
                limits=httpx.Limits(
                    max_connections=int(_config.get("IMAGE_MAX_CONCURRENCY")),
                    max_keepalive_connections=int(
                        _config.get("IMAGE_MAX_CONCURRENCY")
                    ),
                ),
            )


async def shutdown_image_proxy() -> None:
    global _image_http_client
    async with _image_client_lock:
        if _image_http_client is not None:
            await _image_http_client.aclose()
            _image_http_client = None


async def _get_image_http_client() -> httpx.AsyncClient:
    if _image_http_client is None:
        await init_image_proxy()
    if _image_http_client is None:
        raise RuntimeError("Image proxy client failed to initialize")
    return _image_http_client


@asynccontextmanager
async def _image_fetch_lock(image_id: str):
    async with _image_locks_guard:
        state = _image_locks.get(image_id)
        if state is None:
            state = _LockState(lock=asyncio.Lock())
            _image_locks[image_id] = state
        state.users += 1

    acquired = False
    try:
        await state.lock.acquire()
        acquired = True
        yield
    finally:
        if acquired:
            state.lock.release()
        async with _image_locks_guard:
            state.users -= 1
            if state.users == 0:
                _image_locks.pop(image_id, None)


def is_image_field(key: str) -> bool:
    return any(part in key.lower() for part in IMAGE_KEYS)


def _to_plain(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "__dict__"):
        return {
            key: nested
            for key, nested in value.__dict__.items()
            if not key.startswith("_")
        }
    return value


def is_image_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith(IMAGE_EXTENSIONS) or any(
        keyword in path for keyword in IMAGE_PATH_KEYWORDS
    )


def image_id_for_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def register_image_sources(
    source_urls: Iterable[str],
    db: Session | None = None,
) -> dict[str, str]:
    sources = {
        image_id_for_url(url): url
        for url in source_urls
        if url.startswith(("http://", "https://"))
    }
    if not sources:
        return {}

    owns_session = db is None
    session = db or SessionLocal()
    try:
        rows = [
            {"image_id": image_id, "source_url": source_url}
            for image_id, source_url in sources.items()
        ]
        for start in range(0, len(rows), 400):
            session.execute(
                insert(ImageSource)
                .values(rows[start : start + 400])
                .on_conflict_do_nothing(index_elements=["image_id"])
            )
        if owns_session:
            session.commit()
        else:
            session.flush()
        return sources
    except Exception:
        session.rollback()
        raise
    finally:
        if owns_session:
            session.close()


def replace_domain_in_value(value: Any, exclude: list[str] | None = None) -> Any:
    prefix = _config.get("SYSTEM_IMAGE_PREFIX")
    excluded_domains = set(exclude or [])
    discovered_sources: dict[str, str] = {}

    def replace(nested: Any, image_context: bool = False) -> Any:
        nested = _to_plain(nested)

        if isinstance(nested, dict):
            return {
                key: replace(child, image_context or is_image_field(str(key)))
                for key, child in nested.items()
            }
        if isinstance(nested, list):
            return [replace(child, image_context) for child in nested]
        if not isinstance(nested, str):
            return nested
        if not nested.startswith(("http://", "https://")):
            return nested

        parsed = urlparse(nested)
        if parsed.netloc in excluded_domains:
            return nested
        if not image_context and not is_image_url(nested):
            return nested

        image_id = image_id_for_url(nested)
        discovered_sources[image_id] = nested
        return f"{prefix}{image_id}"

    result = replace(value)
    register_image_sources(discovered_sources.values())
    return result


def get_image_source(db: Session, image_id: str) -> ImageSource | None:
    if len(image_id) != 64 or any(char not in "0123456789abcdef" for char in image_id):
        return None
    return db.query(ImageSource).filter(ImageSource.image_id == image_id).first()


def get_cache_path(image_id: str) -> Path:
    return CACHE_DIR / image_id


def _file_etag(path: Path) -> str:
    stat = path.stat()
    value = f"{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _cached_image_from_file(source: ImageSource, path: Path, stale=False) -> CachedImage:
    runtime = _image_runtime_metadata.get(source.image_id)
    content_type = source.content_type or (runtime.content_type if runtime else None) or (
        mimetypes.guess_type(urlparse(source.source_url).path)[0]
        or "application/octet-stream"
    )
    return CachedImage(
        path=path,
        content_type=content_type,
        content_etag=(
            source.content_etag
            or (runtime.content_etag if runtime else None)
            or _file_etag(path)
        ),
        upstream_etag=(
            source.upstream_etag
            or (runtime.upstream_etag if runtime else None)
        ),
        upstream_last_modified=(
            source.upstream_last_modified
            or (runtime.upstream_last_modified if runtime else None)
        ),
        stale=stale,
    )


def _cache_is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    modified_at = datetime.fromtimestamp(path.stat().st_mtime)
    return datetime.now() - modified_at < timedelta(hours=CACHE_EXPIRE_HOURS)


async def fetch_and_cache_image(source: ImageSource) -> CachedImage:
    cache_path = get_cache_path(source.image_id)

    async with _image_fetch_lock(source.image_id):
        if _cache_is_fresh(cache_path):
            return _cached_image_from_file(source, cache_path)

        request_headers = {}
        if cache_path.exists() and source.upstream_etag:
            request_headers["If-None-Match"] = source.upstream_etag
        if cache_path.exists() and source.upstream_last_modified:
            request_headers["If-Modified-Since"] = source.upstream_last_modified

        temporary_path = cache_path.with_name(
            f"{cache_path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        )
        try:
            client = await _get_image_http_client()
            async with _image_fetch_semaphore:
                async with client.stream(
                    "GET",
                    source.source_url,
                    headers=request_headers,
                ) as response:
                    if response.status_code == status.HTTP_304_NOT_MODIFIED:
                        if not cache_path.exists():
                            raise HTTPException(
                                status_code=status.HTTP_502_BAD_GATEWAY,
                                detail="Image source returned 304 without a cache entry",
                            )
                        os.utime(cache_path, None)
                        return _cached_image_from_file(source, cache_path)

                    if response.status_code >= 400:
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Image source returned {response.status_code}",
                        )

                    content_length = response.headers.get("content-length")
                    if content_length and int(content_length) > IMAGE_MAX_BYTES:
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Image exceeds the configured size limit",
                        )

                    source_content_type = response.headers.get(
                        "content-type", ""
                    ).split(";", 1)[0]
                    if source_content_type and not (
                        source_content_type.startswith("image/")
                        or source_content_type
                        in {"application/octet-stream", "binary/octet-stream"}
                    ):
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Image source returned non-image content",
                        )

                    written = 0
                    async with aiofiles.open(temporary_path, "wb") as cache_file:
                        async for chunk in response.aiter_bytes():
                            written += len(chunk)
                            if written > IMAGE_MAX_BYTES:
                                raise HTTPException(
                                    status_code=status.HTTP_502_BAD_GATEWAY,
                                    detail="Image exceeds the configured size limit",
                                )
                            await cache_file.write(chunk)

                    os.replace(temporary_path, cache_path)
                    content_type = source_content_type
                    if not content_type:
                        content_type = (
                            mimetypes.guess_type(urlparse(source.source_url).path)[0]
                            or "application/octet-stream"
                        )

                    cached = CachedImage(
                        path=cache_path,
                        content_type=content_type,
                        content_etag=_file_etag(cache_path),
                        upstream_etag=response.headers.get("etag"),
                        upstream_last_modified=response.headers.get("last-modified"),
                    )
                    _image_runtime_metadata[source.image_id] = cached
                    return cached
        except Exception as exc:
            if cache_path.exists():
                return _cached_image_from_file(source, cache_path, stale=True)
            if isinstance(exc, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch image",
            ) from exc
        finally:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def update_image_source_metadata(
    db: Session,
    source: ImageSource,
    cached: CachedImage,
) -> None:
    values = {
        "content_type": cached.content_type,
        "content_etag": cached.content_etag,
        "upstream_etag": cached.upstream_etag,
        "upstream_last_modified": cached.upstream_last_modified,
    }
    changed = False
    for key, value in values.items():
        if value is not None and getattr(source, key) != value:
            setattr(source, key, value)
            changed = True
    if changed:
        try:
            db.commit()
        except Exception:
            db.rollback()


# Legacy token helpers remain temporarily so previously issued image URLs can
# still be served after the stable image-id endpoint is deployed.
def next_monday_timestamp() -> int:
    today = datetime.now()
    days_ahead = -today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(next_monday.timestamp())


def encrypt_payload(url: str) -> str:
    payload = DecryptedImagePayload(url=url, exp=next_monday_timestamp())
    key = _config.get_image_token_key()
    aesgcm = AESGCM(key)
    plaintext = json.dumps(
        payload.model_dump(), separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    nonce = hashlib.sha256(plaintext).digest()[:12]
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_payload(token: str) -> DecryptedImagePayload:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8"))
        nonce, ciphertext = raw[:12], raw[12:]
        key = _config.get_image_token_key()
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        return DecryptedImagePayload(**json.loads(plaintext.decode("utf-8")))
    except (InvalidTag, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid image token") from exc
