from typing import Optional
from database import EmbyMovie
from sqlalchemy.orm import Session
from utils.extract_code import extract_jav_code


async def _get_admin_user_id() -> Optional[str]:
    from modules.mediaServer.emby import _emby_instance

    info = await _emby_instance.request("/Users/Query")
    for user in info.get("Items", []):
        if user.get("Policy", {}).get("IsAdministrator"):
            return user.get("Id")
    return None


async def get_item_counts_service():
    from modules.mediaServer.emby import _emby_instance

    results = await _emby_instance.request("/Items/Counts", use_header=True)
    return results


async def get_latest_items_service() -> list[dict]:
    from modules.mediaServer.emby import _emby_instance

    user_id = await _get_admin_user_id()
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
    items = await _emby_instance.request(
        f"/Users/{user_id}/Items/Latest", params=params
    )

    result = []
    for item in items:
        item_id = item["Id"]
        server_id = item["ServerId"]

        result.append(
            {
                "name": item["Name"],
                "primary": f"{_emby_instance.emby_url}/Items/{item_id}/Images/Primary",
                "serverId": server_id,
                "indexLink": (
                    f"{_emby_instance.emby_url}/web/index.html#!/item"
                    f"?id={item_id}&context=home&serverId={server_id}"
                ),
                "playbackLink": (
                    f"{_emby_instance.emby_url}/emby/videos/{item_id}/stream.mp4"
                    f"?api_key={_emby_instance.api_key}&Static=true"
                ),
            }
        )
    return result


async def get_resume_items_service() -> list[dict]:
    from modules.mediaServer.emby import _emby_instance

    user_id = await _get_admin_user_id()
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
    items = (
        await _emby_instance.request(f"/Users/{user_id}/Items/Resume", params=params)
    ).get("Items", [])

    result = []
    for item in items:
        item_id = item["Id"]
        server_id = item["ServerId"]

        result.append(
            {
                "name": item["Name"],
                "primary": f"{_emby_instance.emby_url}/Items/{item_id}/Images/Primary",
                "serverId": server_id,
                "indexLink": (
                    f"{_emby_instance.emby_url}/web/index.html#!/item"
                    f"?id={item_id}&context=home&serverId={server_id}"
                ),
                "playbackLink": (
                    f"{_emby_instance.emby_url}/emby/videos/{item_id}/stream.mp4"
                    f"?api_key={_emby_instance.api_key}&Static=true"
                ),
            }
        )
    return result


async def get_views_service() -> list[dict]:
    from modules.mediaServer.emby import _emby_instance

    user_id = await _get_admin_user_id()
    if not user_id:
        return []

    items = (await _emby_instance.request(f"/Users/{user_id}/Views")).get("Items", [])

    result = []
    for item in items:
        name = item.get("Name")
        item_id = item.get("Id")
        server_id = item.get("ServerId")
        primary = f"{_emby_instance.emby_url}/Items/{item_id}/Images/Primary"
        indexLink = f"{_emby_instance.emby_url}/web/index.html#!/videos?serverId={server_id}&parentId={item_id}"

        result.append(
            {
                "name": name,
                "primary": primary,
                "serverId": server_id,
                "indexLink": indexLink,
            }
        )
    return result


async def get_all_movies_service() -> list[dict]:
    from modules.mediaServer.emby import _emby_instance

    user_id = await _get_admin_user_id()
    if not user_id:
        return []

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

    items = (
        await _emby_instance.request(f"/Users/{user_id}/Items", params=params)
    ).get("Items", [])

    result = []
    for item in items:
        item_id = item.get("Id")
        server_id = item.get("ServerId")
        result.append(
            {
                "name": item.get("Name"),
                "primary": f"{_emby_instance.emby_url}/Items/{item_id}/Images/Primary",
                "serverId": server_id,
                "indexLink": f"{_emby_instance.emby_url}/web/index.html#!/videos?serverId={server_id}&parentId={item_id}",
                "ProductionYear": item.get("ProductionYear"),
            }
        )
    return result


async def exists_service(db: Session, title: str):

    jav_code = extract_jav_code(title)
    movie = db.query(EmbyMovie).filter(EmbyMovie.name.ilike(f"%{jav_code}%")).first()
    exists_flag, index_link = (True, movie.indexLink) if movie else (False, None)

    return {"exists": exists_flag, "indexLink": index_link}
