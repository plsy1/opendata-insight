import httpx
from typing import Optional


class EmbyService:
    def __init__(self, emby_url: str, api_key: str):
        self.emby_url = emby_url
        self.api_key = api_key
        self.client: Optional[httpx.AsyncClient] = None

    async def start(self):
        if not self.emby_url or not self.api_key:
            return
        self.client = httpx.AsyncClient(timeout=20.0)

    async def shutdown(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def request(self, path: str, params=None, method="GET", use_header=True):
        if not self.client:
            raise RuntimeError("EmbyService not started")

        if params is None:
            params = {}

        url = f"{self.emby_url}/emby{path}"
        headers = {}

        if use_header:
            headers["X-Emby-Token"] = self.api_key
        else:
            params["api_key"] = self.api_key

        resp = await self.client.request(method, url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


_emby_instance: Optional[EmbyService] = None


async def init_emby_service(emby_url: str, api_key: str) -> EmbyService:
    global _emby_instance
    if _emby_instance is None:
        _emby_instance = EmbyService(emby_url, api_key)
        await _emby_instance.start()
    return _emby_instance


async def shutdown_emby_service():
    global _emby_instance
    if _emby_instance:
        await _emby_instance.shutdown()
        _emby_instance = None
