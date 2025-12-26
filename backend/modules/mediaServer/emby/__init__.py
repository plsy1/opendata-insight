import requests
import json
from typing import List, Dict
from core.config import _config
from core.database import get_db, EmbyMovie
from core.system.model import DecryptedImagePayload
from core.system import encrypt_payload
import time


def is_movie_in_db_partial(title: str):
    db = next(get_db())
    try:
        movie = db.query(EmbyMovie).filter(EmbyMovie.name.ilike(f"%{title}%")).first()
        if movie:
            return True, movie.indexLink
        else:
            return False, None
    finally:
        db.close()


def emby_request(path: str, params=None, method="GET", use_header=True) -> List[Dict]:
    """
    发送带 Emby API key 的请求
    :param path: API 路径，比如 '/System/Info'
    :param params: 查询参数字典
    :param method: HTTP 方法 GET / POST / ...
    :param use_header: True 使用 Header 认证，False 使用 Query 认证
    """
    if params is None:
        params = {}

    EMBY_URL = _config.get("EMBY_URL")
    EMBY_API_KEY = _config.get("EMBY_API_KEY")

    url = f"{EMBY_URL}/emby{path}"

    headers = {}
    if use_header:
        headers["X-Emby-Token"] = EMBY_API_KEY
    else:
        params["api_key"] = EMBY_API_KEY

    response = requests.request(method, url, headers=headers, params=params)
    response.raise_for_status()
    return json.loads(response.text)


def emby_get_userId_of_administrator() -> str:
    try:
        info = emby_request("/Users/Query", use_header=True)
        users = info.get("Items")
        for user in users:
            if user.get("Policy").get("IsAdministrator") == True:
                return user.get("Id")
    except Exception as e:
        return


def emby_get_item_counts() -> Dict:
    try:
        info = emby_request("/Items/Counts", use_header=True)
        return info
    except Exception as e:
        return


def emby_get_latest_items() -> List[Dict]:
    params = {
        "Recursive": "true",
        "Fields": "BasicSyncInfo,CanDelete,CanDownload,PrimaryImageAspectRatio,ProductionYear",
        "ImageTypeLimit": 1,
        "EnableImageTypes": "Primary,Backdrop,Thumb",
        "MediaTypes": "Video",
        "Limit": 16,
    }

    EMBY_URL = _config.get("EMBY_URL")
    SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
    result = []

    userId = emby_get_userId_of_administrator()
    info = emby_request(f"/Users/{userId}/Items/Latest", use_header=True, params=params)

    for item in info:
        name = item.get("Name")
        item_id = item.get("Id")
        serverId = item.get("ServerId")

        real_image_url = f"{EMBY_URL}/Items/{item_id}/Images/Primary"

        image_token = encrypt_payload(real_image_url)

        primary = f"{SYSTEM_IMAGE_PREFIX}{image_token}"

        indexLink = (
            f"{EMBY_URL}/web/index.html#!/item?"
            f"id={item_id}&context=home&serverId={serverId}"
        )

        playbackLink = f"{EMBY_URL}/emby/videos/{item_id}/stream.mp4?api_key={_config.get('EMBY_API_KEY')}&Static=true"

        result.append(
            {
                "name": name,
                "primary": primary,
                "serverId": serverId,
                "indexLink": indexLink,
                "playbackLink": playbackLink,
            }
        )

    return result


def emby_get_resume_items() -> List[Dict]:
    params = {
        "Recursive": "true",
        "Fields": "BasicSyncInfo,CanDelete,CanDownload,PrimaryImageAspectRatio,ProductionYear",
        "ImageTypeLimit": 1,
        "EnableImageTypes": "Primary,Backdrop,Thumb",
        "MediaTypes": "Video",
        "Limit": 16,
    }
    try:
        EMBY_URL = _config.get("EMBY_URL")
        result = []
        userId = emby_get_userId_of_administrator()
        info = emby_request(
            f"/Users/{userId}/Items/Resume", use_header=True, params=params
        )
        SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
        for item in info.get("Items"):
            name = item.get("Name")
            item_id = item.get("Id")
            serverId = item.get("ServerId")

            real_image_url = f"{EMBY_URL}/Items/{item_id}/Images/Primary"


            image_token = encrypt_payload(real_image_url)

            primary = f"{SYSTEM_IMAGE_PREFIX}{image_token}"

            indexLink = f"{EMBY_URL}/web/index.html#!/item?id={item_id}&context=home&serverId={serverId}"
            PlayedPercentage = item.get("UserData").get("PlayedPercentage")
            ProductionYear = item.get("ProductionYear")
            playbackLink = f"{EMBY_URL}/emby/videos/{item_id}/stream.mp4?api_key={_config.get('EMBY_API_KEY')}&Static=true"
            result.append(
                {
                    "name": name,
                    "primary": primary,
                    "serverId": serverId,
                    "indexLink": indexLink,
                    "PlayedPercentage": PlayedPercentage,
                    "ProductionYear": ProductionYear,
                    "playbackLink": playbackLink,
                }
            )
        return result
    except Exception as e:
        return


def emby_get_views() -> List[Dict]:
    try:
        SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
        EMBY_URL = _config.get("EMBY_URL")
        result = []
        userId = emby_get_userId_of_administrator()
        info = emby_request(f"/Users/{userId}/Views", use_header=True)
        items = info.get("Items")
        for item in items:
            name = item.get("Name")
            item_id = item.get("Id")
            ServerId = item.get("ServerId")

            real_image_url = f"{EMBY_URL}/Items/{item_id}/Images/Primary"


            image_token = encrypt_payload(real_image_url)

            primary = f"{SYSTEM_IMAGE_PREFIX}{image_token}"

            indexLink = f"{EMBY_URL}/web/index.html#!/videos?serverId={ServerId}&parentId={item_id}"
            result.append(
                {
                    "name": name,
                    "primary": primary,
                    "serverId": ServerId,
                    "indexLink": indexLink,
                }
            )

        return result
    except Exception as e:
        return


def emby_get_all_movies() -> List[Dict]:
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
    try:
        EMBY_URL = _config.get("EMBY_URL")
        userId = emby_get_userId_of_administrator()

        info = emby_request(f"/Users/{userId}/Items", use_header=True, params=params)

        result = []
        for item in info.get("Items", []):
            name = item.get("Name")
            id = item.get("Id")
            serverId = item.get("ServerId")
            SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
            primary = f"{SYSTEM_IMAGE_PREFIX}{EMBY_URL}/Items/{id}/Images/Primary"
            indexLink = f"{EMBY_URL}/web/index.html#!/item?id={id}&context=home&serverId={serverId}"
            ProductionYear = item.get("ProductionYear")

            result.append(
                {
                    "name": name,
                    "primary": primary,
                    "serverId": serverId,
                    "indexLink": indexLink,
                    "ProductionYear": ProductionYear,
                }
            )

        return result

    except Exception as e:
        print(f"Error: {e}")
        return []
