import requests
from typing import Optional
from services.system import encrypt_payload
from database import get_db, EmbyMovie


class EmbyService:
    def __init__(self, emby_url: str, api_key: str):
        self.emby_url = emby_url
        self.api_key = api_key
        self.session: Optional[requests.Session] = None

    async def start(self):
        if not self.emby_url or not self.api_key:
            return
        self.session = requests.Session()

    async def shutdown(self):
        if self.session:
            self.session.close()
            self.session = None

    # ---------- DB ----------
    def is_movie_in_db_partial(self, title: str):
        db = next(get_db())
        try:
            movie = (
                db.query(EmbyMovie).filter(EmbyMovie.name.ilike(f"%{title}%")).first()
            )
            return (True, movie.indexLink) if movie else (False, None)
        finally:
            db.close()

    def request(self, path: str, params=None, method="GET", use_header=True):
        if not self.session:
            raise RuntimeError("EmbyService not started")

        if params is None:
            params = {}

        url = f"{self.emby_url}/emby{path}"
        headers = {}

        if use_header:
            headers["X-Emby-Token"] = self.api_key
        else:
            params["api_key"] = self.api_key

        resp = self.session.request(
            method, url, headers=headers, params=params, timeout=20
        )
        resp.raise_for_status()
        return resp.json()

    # ---------- Users ----------
    def get_admin_user_id(self) -> Optional[str]:
        info = self.request("/Users/Query")
        for user in info.get("Items", []):
            if user.get("Policy", {}).get("IsAdministrator"):
                return user.get("Id")
        return None

    # ---------- Helpers ----------
    def _image_url(self, item_id: str) -> str:
        real = f"{self.emby_url}/Items/{item_id}/Images/Primary"
        token = encrypt_payload(real)
        return f"{self.image_prefix}{token}"

    # ---------- APIs ----------
    def get_latest_items(self) -> list[dict]:
        user_id = self.get_admin_user_id()
        if not user_id:
            return []

        params = {"Recursive": "true", "MediaTypes": "Video", "Limit": 16}
        items = self.request(f"/Users/{user_id}/Items/Latest", params=params)

        result = []
        for item in items:
            item_id = item["Id"]
            server_id = item["ServerId"]

            result.append(
                {
                    "name": item["Name"],
                    "primary": self._image_url(item_id),
                    "serverId": server_id,
                    "indexLink": (
                        f"{self.emby_url}/web/index.html#!/item"
                        f"?id={item_id}&context=home&serverId={server_id}"
                    ),
                    "playbackLink": (
                        f"{self.emby_url}/emby/videos/{item_id}/stream.mp4"
                        f"?api_key={self.api_key}&Static=true"
                    ),
                }
            )
        return result


_emby_service: EmbyService | None = None


async def init_emby_service(emby_url: str, api_key: str) -> EmbyService:
    global _emby_service
    if _emby_service is None:
        _emby_service = EmbyService(
            emby_url=emby_url,
            api_key=api_key,
        )
        await _emby_service.start()
    return _emby_service


async def shutdown_emby_service():
    global _emby_service
    if _emby_service:
        await _emby_service.shutdown()
        _emby_service = None
