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


async def parse_actor_information(url: str) -> ActorDataOut:
    try:
        data = ActorDataOut()
        content = await _get_raw_html(url)
        soup = BeautifulSoup(content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag:
            tmp = json.loads(script_tag.string)
            page_props = tmp["props"]["pageProps"]
            data.name = page_props.get("name", {})

            talent = page_props.get("talent", {})
            primary = talent.get("primary", {})
            data.avatar_url = f'{primary.get("image_url")}'

            fanza = (primary.get("meta") or {}).get("fanza") or {}
            for k, v in fanza.items():
                if hasattr(data, k):
                    setattr(data, k, v)

            actors = talent.get("actors", [])
            data.aliases = [actor.get("name") for actor in actors if actor.get("name")]

        data.social_media = _get_social_media_links(soup)

        return data

    except Exception as e:
        print(e)


async def parse_movie_lists(url: str) -> list[MoviePoster]:
    try:
        content = await _get_raw_html(url)

        soup = BeautifulSoup(content, "html.parser")
        movie_elements = soup.find_all(
            "div",
            class_="bg-base border border-light rounded-lg overflow-hidden h-full",
        )

        movies = []
        for movie in movie_elements:
            id_tag = movie.find("span", class_="font-bold text-gray-500")
            movie_id = id_tag.get_text(strip=True) if id_tag else ""

            title_tag = movie.find(
                "a", class_="text-md font-bold btn-ghost rounded-lg m-1 line-clamp-5"
            )
            if not title_tag:
                title_tag = movie.find(
                    "a",
                    class_="text-md font-bold btn-ghost rounded-lg m-1 line-clamp-3",
                )

            title = title_tag.get_text(strip=True) if title_tag else ""
            link = title_tag.get("href", "") if title_tag else ""
            link = link.split("/")[-1]

            date_tag = movie.find("a", class_="block font-bold")
            date = date_tag.get_text(strip=True) if date_tag else ""

            img_tag = movie.find("img", loading="lazy")
            img_url = img_tag.get("src", "") if img_tag else ""
            if img_url:
                img_url = img_url.replace("ps.", "pl.")
            actors = [
                a.get_text(strip=True)
                for a in movie.find_all("a", class_="chip chip-sm")
            ]

            movies.append(
                MoviePoster(
                    id=movie_id,
                    title=title,
                    full_id=link,
                    release_date=date,
                    img_url=img_url,
                    actors=actors,
                )
            )

        return movies
    except Exception as e:
        print(e)


def _get_social_media_links(soup) -> list[SocialMedia]:
    social_media_links = []

    social_media_div = soup.find("div", class_="group/social col-span-2 mt-4")
    if not social_media_div:
        return social_media_links

    for tooltip in social_media_div.find_all("div", class_="tooltip"):
        link_tag = tooltip.find("a")
        if link_tag:
            href = link_tag.get("href")
            username = tooltip.get("data-tip")
            social_media_links.append(
                SocialMedia(
                    platform=_get_platform_from_link(href),
                    username=username or "",
                    link=href or None,
                )
            )

    return social_media_links


def _get_platform_from_link(link: str):
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
        response = await page.goto(url, timeout=5000)
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
        response = await page.goto(url, timeout=5000)
        status = response.status
        if status == 403:
            raise HTTPException(status_code=status, detail="403")
        content = await page.content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"页面请求失败: {str(e)}")
    finally:
        await page.close()

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

