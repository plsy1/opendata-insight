import json
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from fastapi import HTTPException

from schemas.actor import ActorDataOut, AvbaseIndexActorOut, SocialMedia
from schemas.avbase import MoviePoster


ACTOR_METADATA_FIELDS = {
    "birthday",
    "height",
    "bust",
    "waist",
    "hip",
    "cup",
    "hobby",
    "prefectures",
    "blood_type",
}


def parse_min_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None

    try:
        normalized = date_str.split(" (")[0].split(" GMT")[0]
        dt = datetime.strptime(normalized, "%a %b %d %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def extract_page_props(content: str) -> dict:
    soup = BeautifulSoup(content, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag or not script_tag.string:
        raise HTTPException(status_code=502, detail="AvBase 页面缺少 __NEXT_DATA__")

    try:
        payload = json.loads(script_tag.string)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="AvBase 页面数据解析失败") from exc

    page_props = payload.get("props", {}).get("pageProps")
    if not isinstance(page_props, dict):
        raise HTTPException(status_code=502, detail="AvBase 页面数据结构无效")
    return page_props


def parse_actor_information(content: str) -> ActorDataOut:
    soup = BeautifulSoup(content, "html.parser")
    page_props = extract_page_props(content)

    talent = page_props.get("talent") or {}
    if not isinstance(talent, dict):
        raise HTTPException(status_code=502, detail="AvBase 演员数据结构无效")

    primary = talent.get("primary") or {}
    if not isinstance(primary, dict):
        raise HTTPException(status_code=502, detail="AvBase 演员数据结构无效")

    name = page_props.get("name") or primary.get("name")
    if not name:
        raise HTTPException(status_code=404, detail="未找到演员信息")

    data = ActorDataOut(
        name=name,
        avatar_url=primary.get("image_url"),
        ruby=primary.get("ruby") or page_props.get("ruby"),
    )

    primary_meta = primary.get("meta") or {}
    talent_meta = talent.get("meta") or {}
    if not isinstance(primary_meta, dict):
        primary_meta = {}
    if not isinstance(talent_meta, dict):
        talent_meta = {}

    _apply_actor_metadata(data, primary_meta.get("fanza"))
    _apply_actor_metadata(data, talent_meta.get("fanza"))

    basic_info = talent_meta.get("basic_info") or {}
    if not isinstance(basic_info, dict):
        basic_info = {}
    _apply_actor_metadata(data, basic_info.get("fanza"))
    _apply_actor_metadata(data, basic_info)

    actors = talent.get("actors") or []
    data.aliases = [
        actor.get("name")
        for actor in actors
        if isinstance(actor, dict) and actor.get("name")
    ]
    data.social_media = _merge_social_media(
        _get_social_media_links(soup),
        _social_media_from_metadata(talent_meta),
    )
    return data


def parse_movie_list(content: str) -> list[MoviePoster]:
    soup = BeautifulSoup(content, "html.parser")
    page_props = extract_page_props(content)

    if "works" in page_props:
        works = page_props.get("works") or []
        if not isinstance(works, list):
            raise HTTPException(status_code=502, detail="AvBase 作品数据结构无效")
        return [
            _movie_poster_from_work(work) for work in works if isinstance(work, dict)
        ]
    return _parse_movie_cards_from_dom(soup)


def parse_movie_information(content: str) -> dict:
    work = extract_page_props(content).get("work")
    if not isinstance(work, dict) or not work:
        raise HTTPException(status_code=404, detail="未找到作品信息")
    return work


def parse_actor_lists(
    content: str,
) -> tuple[list[AvbaseIndexActorOut], list[AvbaseIndexActorOut]]:
    page_props = extract_page_props(content)
    newbie_talents_raw = page_props.get("newbie_talents") or []
    popular_talents_raw = page_props.get("popular_talents") or []

    newbie_talents = []
    for item in newbie_talents_raw:
        if not isinstance(item, dict):
            continue
        for actor in item.get("actors") or []:
            if isinstance(actor, dict) and actor.get("name"):
                newbie_talents.append(
                    AvbaseIndexActorOut(
                        name=actor["name"], avatar_url=actor.get("image_url")
                    )
                )

    popular_talents = []
    for item in popular_talents_raw:
        actors = item.get("actors") if isinstance(item, dict) else None
        if not actors or not isinstance(actors[0], dict) or not actors[0].get("name"):
            continue
        popular_talents.append(
            AvbaseIndexActorOut(
                name=actors[0]["name"], avatar_url=actors[0].get("image_url")
            )
        )
    return newbie_talents, popular_talents


def parse_release_works(content: str) -> list[dict]:
    works = extract_page_props(content).get("works") or []
    if not isinstance(works, list):
        raise HTTPException(status_code=502, detail="AvBase 发布数据结构无效")
    return [work for work in works if isinstance(work, dict)]


def _apply_actor_metadata(data: ActorDataOut, metadata: object) -> None:
    if not isinstance(metadata, dict):
        return
    for key, value in metadata.items():
        if key in ACTOR_METADATA_FIELDS and value not in (None, ""):
            setattr(data, key, value)


def _social_media_from_metadata(metadata: object) -> list[SocialMedia]:
    if not isinstance(metadata, dict):
        return []

    social_media = []
    for item in metadata.get("sns", []):
        if not isinstance(item, dict):
            continue
        platform_name = str(item.get("sns") or item.get("platform") or "")
        username = str(item.get("id") or item.get("username") or "")
        link = item.get("url") or item.get("link") or _social_media_url(
            platform_name, username
        )
        if platform_name and link:
            social_media.append(
                SocialMedia(
                    platform=_normalize_platform_name(platform_name),
                    username=username,
                    link=str(link),
                )
            )
    return social_media


def _normalize_platform_name(platform: str) -> str:
    return {
        "x": "Twitter",
        "twitter": "Twitter",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "rss": "RSS",
    }.get(platform.lower(), platform.capitalize())


def _social_media_url(platform: str, username: str) -> Optional[str]:
    if not username:
        return None
    username = username.lstrip("@")
    normalized = platform.lower()
    if normalized in ("x", "twitter"):
        return f"https://x.com/{username}"
    if normalized == "instagram":
        return f"https://www.instagram.com/{username}"
    if normalized == "tiktok":
        return f"https://www.tiktok.com/@{username}"
    if normalized == "youtube":
        return f"https://www.youtube.com/@{username}"
    return None


def _merge_social_media(*groups: list[SocialMedia]) -> list[SocialMedia]:
    merged = []
    seen = set()
    for group in groups:
        for item in group:
            key = item.link or f"{item.platform}:{item.username}"
            if key not in seen:
                seen.add(key)
                merged.append(item)
    return merged


def _actor_name(actor: object) -> Optional[str]:
    if isinstance(actor, str):
        return actor
    if not isinstance(actor, dict):
        return None
    if actor.get("name"):
        return str(actor["name"])
    return _actor_name(actor.get("actor"))


def _movie_poster_from_work(work: dict) -> MoviePoster:
    work_id = str(work.get("work_id") or "")
    prefix = str(work.get("prefix") or "")
    products = [p for p in (work.get("products") or []) if isinstance(p, dict)]
    primary_product = products[0] if products else {}

    img_url = next(
        (product.get("image_url") for product in products if product.get("image_url")),
        None,
    )
    if not img_url:
        img_url = next(
            (
                product.get("thumbnail_url")
                for product in products
                if product.get("thumbnail_url")
            ),
            "",
        ).replace("ps.jpg", "pl.jpg")

    actor_names = []
    for actor in (work.get("actors") or []) + (work.get("casts") or []):
        name = _actor_name(actor)
        if name and name not in actor_names:
            actor_names.append(name)

    return MoviePoster(
        id=work_id,
        title=str(primary_product.get("title") or work.get("title") or ""),
        full_id=f"{prefix}:{work_id}" if prefix else work_id,
        release_date=parse_min_date(
            primary_product.get("date") or work.get("min_date")
        )
        or "",
        img_url=str(img_url or ""),
        actors=actor_names,
    )


def _parse_movie_cards_from_dom(soup: BeautifulSoup) -> list[MoviePoster]:
    movie_elements = soup.select(
        "div.bg-base.border.border-light.rounded-lg.overflow-hidden.h-full, "
        "div.bg-background.border.border-light.rounded-lg.overflow-hidden.h-full"
    )
    movies = []
    for movie in movie_elements:
        title_tag = movie.find(
            "a",
            href=lambda href: href
            and href.startswith("/works/")
            and not href.startswith("/works/date/"),
        )
        if not title_tag:
            continue

        full_id = title_tag.get("href", "").split("/")[-1]
        date_tag = movie.find(
            "a", href=lambda href: href and href.startswith("/works/date/")
        )
        img_tag = movie.find("img", loading="lazy")
        img_url = img_tag.get("src", "") if img_tag else ""

        actors = []
        for actor_tag in movie.find_all(
            "a", href=lambda href: href and href.startswith("/talents/")
        ):
            actor_name = actor_tag.get_text(strip=True)
            if actor_name and actor_name not in actors:
                actors.append(actor_name)

        movies.append(
            MoviePoster(
                id=full_id.split(":", 1)[-1],
                title=title_tag.get_text(strip=True),
                full_id=full_id,
                release_date=date_tag.get_text(strip=True) if date_tag else "",
                img_url=img_url.replace("ps.jpg", "pl.jpg"),
                actors=actors,
            )
        )
    return movies


def _get_social_media_links(soup: BeautifulSoup) -> list[SocialMedia]:
    social_media_div = soup.find("div", class_="group/social")
    if not social_media_div:
        return []

    social_media_links = []
    for link_tag in social_media_div.find_all("a", href=True):
        href = link_tag.get("href") or ""
        tooltip = link_tag.find_parent(attrs={"data-tip": True})
        username = tooltip.get("data-tip") if tooltip else ""
        social_media_links.append(
            SocialMedia(
                platform=_get_platform_from_link(href),
                username=username or "",
                link=href,
            )
        )
    return social_media_links


def _get_platform_from_link(link: str) -> str:
    if "twitter.com" in link or "x.com" in link:
        return "Twitter"
    if "instagram.com" in link:
        return "Instagram"
    if "tiktok.com" in link:
        return "TikTok"
    if "avbase.net" in link:
        return "RSS"
    return "Unknown"
