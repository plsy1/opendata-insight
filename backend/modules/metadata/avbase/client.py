import asyncio
from typing import Optional

import httpx
from fastapi import HTTPException

from config import _config


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


def _config_int(name: str, default: int) -> int:
    try:
        return int(_config.get(name, default))
    except (TypeError, ValueError):
        return default


def _config_float(name: str, default: float) -> float:
    try:
        return float(_config.get(name, default))
    except (TypeError, ValueError):
        return default


class AvbaseClient:
    def __init__(
        self,
        *,
        max_concurrency: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
        http_retries: Optional[int] = None,
    ):
        concurrency = max_concurrency or _config_int("AVBASE_MAX_CONCURRENCY", 4)
        self.timeout_seconds = timeout_seconds or _config_float(
            "AVBASE_HTTP_TIMEOUT_SECONDS", 10.0
        )
        self.http_retries = (
            http_retries
            if http_retries is not None
            else _config_int("AVBASE_HTTP_RETRIES", 1)
        )
        self._semaphore = asyncio.Semaphore(max(1, concurrency))
        self._http_client: Optional[httpx.AsyncClient] = None
        self._http_client_lock = asyncio.Lock()

    async def fetch_html(self, url: str) -> str:
        async with self._semaphore:
            last_http_error: Optional[HTTPException] = None

            for attempt in range(self.http_retries + 1):
                try:
                    content = await self._fetch_http(url)
                    if self._contains_next_data(content):
                        return content
                    last_http_error = HTTPException(
                        status_code=502,
                        detail="AvBase HTTP 响应缺少 __NEXT_DATA__",
                    )
                except HTTPException as exc:
                    if exc.status_code == 404:
                        raise
                    last_http_error = exc
                except Exception as exc:
                    last_http_error = HTTPException(
                        status_code=502,
                        detail=f"AvBase HTTP 请求失败: {exc}",
                    )

                if attempt < self.http_retries:
                    await asyncio.sleep(0.25 * (2**attempt))

            try:
                content = await self._fetch_browser(url)
                if not self._contains_next_data(content):
                    raise HTTPException(
                        status_code=502,
                        detail="AvBase 浏览器响应缺少 __NEXT_DATA__",
                    )
                return content
            except HTTPException as exc:
                if exc.status_code == 404:
                    raise
                http_detail = last_http_error.detail if last_http_error else "未知错误"
                raise HTTPException(
                    status_code=502,
                    detail=f"AvBase 请求失败: HTTP={http_detail}; Browser={exc.detail}",
                ) from exc
            except Exception as exc:
                http_detail = last_http_error.detail if last_http_error else "未知错误"
                raise HTTPException(
                    status_code=502,
                    detail=f"AvBase 请求失败: HTTP={http_detail}; Browser={exc}",
                ) from exc

    async def close(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is not None:
            return self._http_client

        async with self._http_client_lock:
            if self._http_client is None:
                self._http_client = httpx.AsyncClient(
                    follow_redirects=True,
                    headers=DEFAULT_HEADERS,
                    timeout=self.timeout_seconds,
                )
        return self._http_client

    async def _fetch_http(self, url: str) -> str:
        client = await self._get_http_client()
        try:
            response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"AvBase HTTP 请求失败: {exc}",
            ) from exc

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="AvBase 页面不存在")
        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"AvBase HTTP 状态码 {response.status_code}",
            )
        return response.text

    async def _fetch_browser(self, url: str) -> str:
        from modules.playwright import init_playwright_service

        playwright_service = await init_playwright_service()
        context = await playwright_service.get_context()
        page = await context.new_page()
        try:
            response = await page.goto(
                url,
                timeout=int(self.timeout_seconds * 1000),
                wait_until="domcontentloaded",
            )
            if response is None:
                raise HTTPException(status_code=502, detail="AvBase 浏览器无响应")
            if response.status == 404:
                raise HTTPException(status_code=404, detail="AvBase 页面不存在")
            if response.status >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"AvBase 浏览器状态码 {response.status}",
                )
            return await page.content()
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"AvBase 浏览器请求失败: {exc}",
            ) from exc
        finally:
            await page.close()
            await context.close()

    @staticmethod
    def _contains_next_data(content: str) -> bool:
        return 'id="__NEXT_DATA__"' in content or "id='__NEXT_DATA__'" in content


avbase_client = AvbaseClient()


async def shutdown_avbase_client() -> None:
    await avbase_client.close()
