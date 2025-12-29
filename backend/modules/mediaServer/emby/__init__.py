import requests
from typing import Optional


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

    def _get_admin_user_id(self) -> Optional[str]:
        info = self.request("/Users/Query")
        for user in info.get("Items", []):
            if user.get("Policy", {}).get("IsAdministrator"):
                return user.get("Id")
        return None

    def get_latest_items(self) -> list[dict]:
        user_id = self._get_admin_user_id()
        if not user_id:
            return []

        params = {
            "Recursive": "true",
            "Fields": "BasicSyncInfo,CanDelete,CanDownload,PrimaryImageAspectRatio,ProductionYear",
            "ImageTypeLimit": 1,
            "EnableImageTypes": "Primary,Backdrop,Thumb",
            "MediaTypes": "Video",
            "Limit": 16,
        }
        items = self.request(f"/Users/{user_id}/Items/Latest", params=params)

        result = []
        for item in items:
            print(item)
            item_id = item["Id"]
            server_id = item["ServerId"]

            result.append(
                {
                    "name": item["Name"],
                    "primary": f"{self.emby_url}/Items/{item_id}/Images/Primary",
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

    def get_resume_items(self) -> list[dict]:
        user_id = self._get_admin_user_id()
        if not user_id:
            return []

        params = {
            "Recursive": "true",
            "Fields": "BasicSyncInfo,CanDelete,CanDownload,PrimaryImageAspectRatio,ProductionYear",
            "ImageTypeLimit": 1,
            "EnableImageTypes": "Primary,Backdrop,Thumb",
            "MediaTypes": "Video",
            "Limit": 16,
        }
        items = self.request(f"/Users/{user_id}/Items/Resume", params=params).get(
            "Items"
        )

        result = []
        for item in items:
            item_id = item["Id"]
            server_id = item["ServerId"]

            result.append(
                {
                    "name": item["Name"],
                    "primary": f"{self.emby_url}/Items/{item_id}/Images/Primary",
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

    def get_views(self) -> list[dict]:
        user_id = self._get_admin_user_id()
        if not user_id:
            return []

        items = self.request(f"/Users/{user_id}/Views").get("Items")

        result = []

        for item in items:
            name = item.get("Name")
            item_id = item.get("Id")
            ServerId = item.get("ServerId")
            primary = f"{self.emby_url}/Items/{item_id}/Images/Primary"

            indexLink = f"{self.emby_url}/web/index.html#!/videos?serverId={ServerId}&parentId={item_id}"
            result.append(
                {
                    "name": name,
                    "primary": primary,
                    "serverId": ServerId,
                    "indexLink": indexLink,
                }
            )

        return result

    def get_all_movies(self) -> list[dict]:
        params = {
            "Recursive": "true",
            "IncludeItemTypes": "Movie",
            "Fields": "BasicSyncInfo,CanDelete,CanDownload,PrimaryImageAspectRatio,ProductionYear",
            "ImageTypeLimit": 1,
            "EnableImageTypes": "Primary,Backdrop,Thumb",
            "Limit": 500,
            "SortBy": "DateCreated,SortName",
            "SortOrder": "Descending",
        }

        user_id = self._get_admin_user_id()
        if not user_id:
            return []

        items = self.request(f"/Users/{user_id}/Items", params=params).get("Items")

        result = []

        for item in items:
            name = item.get("Name")
            item_id = item.get("Id")
            ServerId = item.get("ServerId")
            primary = f"{self.emby_url}/Items/{item_id}/Images/Primary"
            indexLink = f"{self.emby_url}/web/index.html#!/videos?serverId={ServerId}&parentId={item_id}"
            ProductionYear = item.get("ProductionYear")
            result.append(
                {
                    "name": name,
                    "primary": primary,
                    "serverId": ServerId,
                    "indexLink": indexLink,
                    "ProductionYear": ProductionYear,
                }
            )

        return result


_emby_instance: EmbyService | None = None


async def init_emby_service(emby_url: str, api_key: str) -> EmbyService:
    global _emby_instance
    if _emby_instance is None:
        _emby_instance = EmbyService(
            emby_url=emby_url,
            api_key=api_key,
        )
        await _emby_instance.start()
    return _emby_instance


async def shutdown_emby_service():
    global _emby_instance
    if _emby_instance:
        await _emby_instance.shutdown()
        _emby_instance = None
