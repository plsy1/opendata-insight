from fastapi import HTTPException
from io import IOBase
from datetime import datetime, timedelta
import os
import httpx
from urllib.parse import urlparse
from typing import Any, List
from config import _config
from services.system.model import DecryptedImagePayload
import aiofiles
import json
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CACHE_EXPIRE_HOURS = _config.get("CACHE_EXPIRE_HOURS")

CACHE_DIR = BASE_DIR / _config.get("CACHE_DIR")

os.makedirs(CACHE_DIR, exist_ok=True)


def next_monday_timestamp():
    today = datetime.now()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return int(next_monday.timestamp())


def _to_plain(value: Any) -> Any:
    """
    将 ORM / Pydantic / dataclass 转为 dict
    """
    # Pydantic v2
    if hasattr(value, "model_dump"):
        return value.model_dump()

    # Pydantic v1
    if hasattr(value, "dict"):
        return value.dict()

    # SQLAlchemy ORM
    if hasattr(value, "__dict__"):
        return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}

    return value


def replace_domain_in_value(value: Any, exclude: List[str] = None) -> Any:
    """
    递归替换 dict/list 结构中的所有 URL 为 prefix + encrypt_payload(DecryptedImagePayload)
    排除域名列表中的 URL 不做替换
    """

    prefix = _config.get("SYSTEM_IMAGE_PREFIX")

    if exclude is None:
        exclude = [
            "www.mgstage.com",
            "al.dmm.co.jp",
            "x.com",
            "www.instagram.com",
            "www.avbase.net",
            "ja.wikipedia.org",
            "www.tiktok.com",
        ]

    value = _to_plain(value)

    if isinstance(value, dict):
        return {
            k: replace_domain_in_value(v, exclude) for k, v in value.items()
        }
    elif isinstance(value, list):
        return [replace_domain_in_value(v, exclude) for v in value]
    elif isinstance(value, str):
        if value.startswith("http://") or value.startswith("https://"):
            try:
                parsed = urlparse(value)
                if parsed.netloc in exclude:
                    return value
                token = encrypt_payload(value)
                return f"{prefix}{token}"
            except Exception:
                return value
        else:
            return value
    else:
        return value


def get_cache_path(url: str) -> str:
    import hashlib

    hash_name = hashlib.md5(url.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_name}")


async def fetch_and_cache_image(url: str) -> tuple[IOBase, dict]:
    cache_path = get_cache_path(url)

    if os.path.exists(cache_path):
        last_modified = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - last_modified < timedelta(hours=CACHE_EXPIRE_HOURS):
            etag = str(os.path.getmtime(cache_path))
            headers = {
                "Cache-Control": f"public, max-age={CACHE_EXPIRE_HOURS*3600}",
                "ETag": etag,
            }
            return open(cache_path, "rb"), headers
        else:
            os.remove(cache_path)

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Failed to fetch image")

    async with aiofiles.open(cache_path, "wb") as f:
        await f.write(resp.content)

    etag = str(os.path.getmtime(cache_path))
    headers = {
        "Cache-Control": f"public, max-age={CACHE_EXPIRE_HOURS*3600}",
        "ETag": etag,
    }
    return open(cache_path, "rb"), headers


def encrypt_payload(url) -> str:
    """
    payload: DecryptedImagePayload 实例
    返回：URL-safe base64 字符串
    """
    payload = DecryptedImagePayload(url=url, exp=next_monday_timestamp())

    key = _config.get_image_token_key()
    aesgcm = AESGCM(key)

    plaintext = json.dumps(
        payload.model_dump(), separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

    nonce = hashlib.sha256(plaintext).digest()[:12]

    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    token = base64.urlsafe_b64encode(nonce + ciphertext).decode("utf-8")
    return token


def decrypt_payload(token: str) -> DecryptedImagePayload:
    """
    解密 token 并返回 DecryptedImagePayload 实例
    """
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8"))
        nonce, ciphertext = raw[:12], raw[12:]
        key = _config.get_image_token_key()
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        data = json.loads(plaintext.decode("utf-8"))
        payload = DecryptedImagePayload(**data)
        return payload
    except (InvalidTag, ValueError, json.JSONDecodeError) as e:
        raise ValueError("Invalid image token") from e
