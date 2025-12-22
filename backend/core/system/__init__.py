from fastapi import HTTPException
from io import IOBase
from datetime import datetime, timedelta
import os
import httpx
from urllib.parse import urlparse, quote
from typing import Any, List
from core.config import _config
from core.system.model import DecryptedImagePayload
import aiofiles
import json
import base64
import time
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


CACHE_EXPIRE_HOURS = _config.get("CACHE_EXPIRE_HOURS")
CACHE_DIR = _config.get("CACHE_DIR")

os.makedirs(CACHE_DIR, exist_ok=True)


def replace_domain_in_value(value: Any, prefix: str, exclude: List[str] = None) -> Any:
    """
    递归替换 dict/list 结构中的所有 URL 为 prefix + encrypt_payload(DecryptedImagePayload)
    排除域名列表中的 URL 不做替换
    """
    if exclude is None:
        exclude = ["www.mgstage.com", "al.dmm.co.jp"]

    if isinstance(value, dict):
        return {
            k: replace_domain_in_value(v, prefix, exclude) for k, v in value.items()
        }
    elif isinstance(value, list):
        return [replace_domain_in_value(v, prefix, exclude) for v in value]
    elif isinstance(value, str):
        if value.startswith("http://") or value.startswith("https://"):
            try:
                parsed = urlparse(value)
                if parsed.netloc in exclude:
                    return value
                payload = DecryptedImagePayload(
                    url=value,
                    exp=(
                        (int(time.time()) // 3600)
                        + _config.get("SYSTEM_IMAGE_EXPIRE_HOURS")
                    )
                    * 3600,
                    src="auto",
                )
                token = encrypt_payload(payload)
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


def encrypt_payload(payload: DecryptedImagePayload) -> str:
    """
    payload: DecryptedImagePayload 实例
    返回：URL-safe base64 字符串
    """
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
