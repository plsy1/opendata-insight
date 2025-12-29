import requests
import asyncio
from typing import Optional


class Prowlarr:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    async def start(self):
        await asyncio.sleep(0)

    def search(self, query: str, page: int = 1, page_size: int = 10):
        url = f"{self.base_url}/api/v1/search"
        params = {"query": query, "categories": "6000"}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None


_prowlarr_instance: Optional[Prowlarr] = None
_init_lock = asyncio.Lock()


async def init_prowlarr(base_url: str, api_key: str) -> Prowlarr:
    global _prowlarr_instance
    async with _init_lock:
        if _prowlarr_instance is None:
            _prowlarr_instance = Prowlarr(base_url, api_key)
            await _prowlarr_instance.start()
    return _prowlarr_instance


async def shutdown_prowlarr():
    global _prowlarr_instance
    _prowlarr_instance = None
