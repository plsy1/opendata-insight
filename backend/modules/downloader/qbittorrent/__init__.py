import asyncio
from qbittorrentapi import Client
from io import BytesIO
import httpx
from config import _config
from urllib.parse import urlparse


class QB:
    def __init__(self, qb_url: str, username: str, password: str):

        parsed = urlparse(qb_url)

        host = parsed.hostname
        port = parsed.port if parsed.port else (443 if parsed.scheme == "https" else 80)

        self.tags = "kanojo"
        self.random_tag = None
        self.filter = [
            kw.strip()
            for kw in _config.get("QB_KEYWORD_FILTER", "").split(",")
            if kw.strip()
        ]

        self.qb = Client(host=host, port=port, username=username, password=password)

        self._filter_task: asyncio.Task | None = None
        self._stop_filter = False
        self.http_client: httpx.AsyncClient | None = None

    async def start(self):
        self._stop_filter = False
        self._filter_task = asyncio.create_task(self._background_keyword_filter())
        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=20.0)

    async def stop_filter_task(self):
        self._stop_filter = True
        if self._filter_task:
            await self._filter_task
            self._filter_task = None

    async def _background_keyword_filter(self):
        while not self._stop_filter:
            try:
                torrents = await asyncio.to_thread(self.qb.torrents_info, tag=self.tags)
                for t in torrents:
                    torrent_hash = t.hash
                    files = await asyncio.to_thread(
                        self.qb.torrents.files, torrent_hash
                    )
                    if not files:
                        continue
                    deselect_ids = [
                        f.index
                        for f in files
                        if any(kw in f.name.lower() for kw in self.filter)
                    ]
                    if deselect_ids:
                        await asyncio.to_thread(
                            self.qb.torrents.file_priority,
                            torrent_hash=torrent_hash,
                            file_ids=deselect_ids,
                            priority=0,
                        )
            except Exception as e:
                print(f"[QB keyword filter error]: {e}")

            await asyncio.sleep(5)

    async def delete_torrent(self, torrent_hash, delete_files=True):
        return await asyncio.to_thread(
            self.qb.torrents_delete,
            delete_files=delete_files,
            torrent_hashes=torrent_hash,
        )

    async def get_downloading_torrents(self):
        try:
            torrents = await asyncio.to_thread(
                self.qb.torrents_info, status_filter="downloading", tag=self.tags
            )
            return [
                {
                    "name": t.name,
                    "progress": t.progress,
                    "size": t.size,
                    "download_speed": t.dlspeed,
                    "eta": t.eta,
                    "tags": t.tags,
                    "hash": t.hash,
                }
                for t in torrents
            ]
        except Exception as e:
            print("Failed to fetch downloading torrents:", e)
            return []

    async def add_torrent_url(self, download_link, save_path, tags=None):
        if tags is None:
            tags = self.tags
        torrent_options = {"urls": download_link, "tags": tags, "save_path": save_path}
        try:
            return (
                await asyncio.to_thread(self.qb.torrents_add, **torrent_options)
                == "Ok."
            )
        except Exception as e:
            print(f"Error adding torrent: {e}")
            return False

    async def add_torrent_file(self, torrent_name, torrent_data, save_path, tags=None):
        if tags is None:
            tags = self.tags
        torrent_bytes = torrent_data.getvalue()
        torrent_options = {
            "torrent_files": torrent_bytes,
            "tags": tags,
            "save_path": save_path,
            "rename": torrent_name,
        }
        try:
            return (
                await asyncio.to_thread(self.qb.torrents_add, **torrent_options)
                == "Ok."
            )
        except Exception as e:
            print(f"Error adding torrent: {e}")
            return False

    async def download_torrent_file(self, torrent_url):
        if not self.http_client:
            raise RuntimeError("QB http client not started")
        try:
            resp = await self.http_client.get(torrent_url)
            resp.raise_for_status()
            return BytesIO(resp.content)
        except Exception as e:
            print(f"Error downloading torrent: {e}")
            return None

    async def shutdown(self):
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None


_qb_instance: QB | None = None


_qb_lock = asyncio.Lock()


async def init_qb(qb_url: str, username: str, password: str) -> QB:
    global _qb_instance
    async with _qb_lock:
        if _qb_instance is None:
            _qb_instance = QB(qb_url, username, password)
            await _qb_instance.start()
    return _qb_instance


async def shutdown_qb():
    global _qb_instance
    async with _qb_lock:
        if _qb_instance:
            await _qb_instance.shutdown()
            _qb_instance = None
