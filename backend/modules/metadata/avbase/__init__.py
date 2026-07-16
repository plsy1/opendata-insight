import json
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from database import MovieData, MovieProduct
from pydantic import BaseModel
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import HTTPException
from schemas.actor import SocialMedia, ActorDataOut, AvbaseIndexActorOut
from typing import Optional


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


class MoviePoster(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str]


def parse_min_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None

    try:
        date_str = date_str.split(" (")[0].split(" GMT")[0]
        dt = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def _get_page_props(soup: BeautifulSoup) -> dict:
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
        if not platform_name or not link:
            continue

        social_media.append(
            SocialMedia(
                platform=_normalize_platform_name(platform_name),
                username=username,
                link=str(link),
            )
        )

    return social_media


def _normalize_platform_name(platform: str) -> str:
    normalized = platform.lower()
    return {
        "x": "Twitter",
        "twitter": "Twitter",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "youtube": "YouTube",
        "rss": "RSS",
    }.get(normalized, platform.capitalize())


def _social_media_url(platform: str, username: str) -> Optional[str]:
    if not username:
        return None

    normalized = platform.lower()
    if normalized in ("x", "twitter"):
        return f"https://x.com/{username.lstrip('@')}"
    if normalized == "instagram":
        return f"https://www.instagram.com/{username.lstrip('@')}"
    if normalized == "tiktok":
        return f"https://www.tiktok.com/@{username.lstrip('@')}"
    if normalized == "youtube":
        return f"https://www.youtube.com/@{username.lstrip('@')}"
    return None


async def parse_actor_information(url: str) -> ActorDataOut:
    content = await _get_raw_html(url)
    soup = BeautifulSoup(content, "html.parser")
    page_props = _get_page_props(soup)

    talent = page_props.get("talent") or {}
    primary = talent.get("primary") or {}
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


def _merge_social_media(*groups: list[SocialMedia]) -> list[SocialMedia]:
    merged = []
    seen = set()
    for group in groups:
        for item in group:
            key = item.link or f"{item.platform}:{item.username}"
            if key in seen:
                continue
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
    full_id = f"{prefix}:{work_id}" if prefix else work_id

    products = [p for p in (work.get("products") or []) if isinstance(p, dict)]
    primary_product = products[0] if products else {}

    title = primary_product.get("title") or work.get("title") or ""
    release_date = parse_min_date(
        primary_product.get("date") or work.get("min_date")
    ) or ""

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
        )
        img_url = img_url.replace("ps.jpg", "pl.jpg")

    actor_names = []
    for actor in (work.get("actors") or []) + (work.get("casts") or []):
        name = _actor_name(actor)
        if name and name not in actor_names:
            actor_names.append(name)

    return MoviePoster(
        id=work_id,
        title=str(title),
        full_id=full_id,
        release_date=release_date,
        img_url=str(img_url or ""),
        actors=actor_names,
    )


async def parse_movie_lists(url: str) -> list[MoviePoster]:
    content = await _get_raw_html(url)
    soup = BeautifulSoup(content, "html.parser")
    page_props = _get_page_props(soup)

    if "works" in page_props:
        works = page_props.get("works") or []
        if not isinstance(works, list):
            raise HTTPException(status_code=502, detail="AvBase 作品数据结构无效")
        return [
            _movie_poster_from_work(work) for work in works if isinstance(work, dict)
        ]

    return _parse_movie_cards_from_dom(soup)


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
        movie_id = full_id.split(":", 1)[-1]
        date_tag = movie.find(
            "a", href=lambda href: href and href.startswith("/works/date/")
        )
        img_tag = movie.find("img", loading="lazy")
        img_url = img_tag.get("src", "") if img_tag else ""
        if img_url:
            img_url = img_url.replace("ps.jpg", "pl.jpg")

        actors = []
        for actor_tag in movie.find_all(
            "a", href=lambda href: href and href.startswith("/talents/")
        ):
            actor_name = actor_tag.get_text(strip=True)
            if actor_name and actor_name not in actors:
                actors.append(actor_name)

        movies.append(
            MoviePoster(
                id=movie_id,
                title=title_tag.get_text(strip=True),
                full_id=full_id,
                release_date=date_tag.get_text(strip=True) if date_tag else "",
                img_url=img_url,
                actors=actors,
            )
        )

    return movies


def _get_social_media_links(soup) -> list[SocialMedia]:
    social_media_links = []

    social_media_div = soup.find("div", class_="group/social")
    if not social_media_div:
        return social_media_links

    for link_tag in social_media_div.find_all("a", href=True):
        href = link_tag.get("href")
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


def _get_platform_from_link(link: str):
    link = link or ""
    if "twitter.com" in link or "x.com" in link:
        return "Twitter"
    elif "instagram.com" in link:
        return "Instagram"
    elif "tiktok.com" in link:
        return "TikTok"
    elif "avbase.net" in link:
        return "RSS"
    else:
        return "Null"


async def _get_next_data(url: str):
    from modules.playwright import _playwright_service

    context = await _playwright_service.get_context(use_new_fingerprint=True)
    page = await context.new_page()

    try:
        response = await page.goto(url, timeout=5000, wait_until="domcontentloaded")
        status = response.status
        if status == 403:
            raise HTTPException(status_code=status, detail="403 Forbidden")
        content = await page.content()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"页面请求失败: {str(e)}")

    finally:
        await page.close()
        await context.close()

    soup = BeautifulSoup(content, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag:
        raise HTTPException(status_code=500, detail="没有找到 __NEXT_DATA__")
    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON 解析失败")

    return data


async def _get_raw_html(url: str):
    from modules.playwright import _playwright_service

    context = await _playwright_service.get_context()
    page = await context.new_page()
    try:
        response = await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        status = response.status
        if status == 403:
            raise HTTPException(status_code=status, detail="403")
        content = await page.content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"页面请求失败: {str(e)}")
    finally:
        await page.close()
        await context.close()

    return content


async def parse_movie_information(work_id: str) -> dict:
    url = f"https://www.avbase.net/works/{work_id}"
    data = await _get_next_data(url)
    return data.get("props", {}).get("pageProps", {}).get("work", {})


async def parse_actor_lists() -> (
    tuple[list[AvbaseIndexActorOut], list[AvbaseIndexActorOut]]
):
    url = "https://www.avbase.net"
    data = await _get_next_data(url)
    page_props = data.get("props", {}).get("pageProps", {})

    newbie_talents_raw = page_props.get("newbie_talents", [])
    popular_talents_raw = page_props.get("popular_talents", [])

    newbie_talents: list[AvbaseIndexActorOut] = []
    for item in newbie_talents_raw:
        for actor in item.get("actors", []):
            name = actor.get("name")
            avatar_url = actor.get("image_url")
            newbie_talents.append(
                AvbaseIndexActorOut(name=name, avatar_url=avatar_url, isActive=False)
            )

    popular_talents: list[AvbaseIndexActorOut] = []
    for item in popular_talents_raw:
        actors = item.get("actors", [])
        if not actors:
            continue
        actor = actors[0]
        name = actor.get("name")
        avatar_url = actor.get("image_url")
        popular_talents.append(
            AvbaseIndexActorOut(name=name, avatar_url=avatar_url, isActive=False)
        )

    return newbie_talents, popular_talents


async def _get_every_day_release(date_str: str):
    all_works = []

    page = 1
    while True:
        url = f"https://www.avbase.net/works/date/{date_str}?page={page}"
        data = await _get_next_data(url)

        works_data = data.get("props", {}).get("pageProps", {}).get("works", [])

        if not works_data:
            break

        all_works.extend(works_data)
        page += 1

    return all_works


async def fetch_avbase_release_by_date_and_write_db(db: Session, date_str: str):

    all_works = await _get_every_day_release(date_str)

    movie_records = []
    for work_dict in all_works:
        movie_records.append(
            dict(
                work_id=work_dict["work_id"],
                prefix=work_dict.get("prefix", ""),
                title=work_dict.get("title", ""),
                min_date=parse_min_date(work_dict.get("min_date")),
                casts=[c["actor"] for c in work_dict.get("casts", [])],
                actors=work_dict.get("actors", []),
                tags=work_dict.get("tags", []),
                genres=[g["name"] for g in work_dict.get("genres", [])],
            )
        )

    if movie_records:
        stmt = sqlite_insert(MovieData).values(movie_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id"],
            set_={
                "prefix": stmt.excluded.prefix,
                "title": stmt.excluded.title,
                "min_date": stmt.excluded.min_date,
                "casts": stmt.excluded.casts,
                "actors": stmt.excluded.actors,
                "tags": stmt.excluded.tags,
                "genres": stmt.excluded.genres,
            },
        )
        db.execute(stmt)
        db.flush()

    work_ids = [w["work_id"] for w in all_works]
    movie_map = {
        m.work_id: m.id
        for m in db.query(MovieData).filter(MovieData.work_id.in_(work_ids)).all()
    }

    product_records = []
    for work_dict in all_works:
        movie_id = movie_map[work_dict["work_id"]]
        for p in work_dict.get("products", []):
            product_date = parse_min_date(p.get("date"))
            product_records.append(
                dict(
                    product_id=p["product_id"],
                    url=p["url"],
                    image_url=p.get("image_url"),
                    title=p.get("title"),
                    source=p.get("source"),
                    thumbnail_url=p.get("thumbnail_url"),
                    date=product_date,
                    maker=p.get("maker", {}).get("name") if p.get("maker") else None,
                    label=p.get("label", {}).get("name") if p.get("label") else None,
                    series=p.get("series", {}).get("name") if p.get("series") else None,
                    sample_image_urls=p.get("sample_image_urls", []),
                    director=(
                        p.get("iteminfo", {}).get("director")
                        if p.get("iteminfo")
                        else None
                    ),
                    price=(
                        p.get("iteminfo", {}).get("price")
                        if p.get("iteminfo")
                        else None
                    ),
                    volume=(
                        p.get("iteminfo", {}).get("volume")
                        if p.get("iteminfo")
                        else None
                    ),
                    work_id=movie_id,
                )
            )

    if product_records:
        stmt = sqlite_insert(MovieProduct).values(product_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["work_id", "product_id"],
            set_={
                k: stmt.excluded[k] for k in product_records[0].keys() if k != "work_id"
            },
        )
        db.execute(stmt)

    db.commit()
