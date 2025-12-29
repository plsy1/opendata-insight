import json

from datetime import datetime
from bs4 import BeautifulSoup
from fastapi import HTTPException
from schemas.actor import SocialMedia
from config import _config
from services.system import encrypt_payload

from database import MovieData, MovieProduct
from pydantic import BaseModel

from typing import Optional

class Movie(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: list[str]

def parse_min_date(date_str: Optional[str]) -> Optional[str]:
    """
    将日期字符串解析并转换为 'YYYY-MM-DD' 格式。

    示例输入：
        'Wed Dec 25 1964 00:00:00 GMT+0000 (Coordinated Universal Time)'
    返回：
        '1964-12-25'

    如果输入为空或格式不正确，返回 None。
    """
    if not date_str:
        return None

    try:
        date_str = date_str.split(" (")[0].split(" GMT")[0]
        dt = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


async def get_movies(url: str, changeImagePrefix: bool = True) -> list[Movie]:
    try:
        content = await get_raw_html(url)

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

                if changeImagePrefix:
                    SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")

                    image_token = encrypt_payload(img_url)

                    img_url = f"{SYSTEM_IMAGE_PREFIX}{image_token}"

            actors = [
                a.get_text(strip=True)
                for a in movie.find_all("a", class_="chip chip-sm")
            ]

            movies.append(
                Movie(
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


def get_social_media_links(soup) -> list[SocialMedia]:
    """获取社交媒体链接"""
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
                    platform=get_platform_from_link(href),
                    username=username or "",
                    link=href or None,
                )
            )

    return social_media_links


def get_platform_from_link(link: str):
    """根据链接来推测平台名称"""
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


def date_trans(date: str) -> str:
    try:
        dt = datetime.strptime(date[:24], "%a %b %d %Y %H:%M:%S")
        return dt.strftime("%Y/%m/%d")
    except Exception:
        return date


async def get_next_data(url: str):
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


async def get_raw_html(url: str):
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


def get_movie_from_db(db, work_id: str) -> MovieData | None:
    return db.query(MovieData).filter(MovieData.work_id == work_id).first()


# ---------------------------
# API 抓取
# ---------------------------
async def fetch_work_data(canonical_id: str) -> dict:
    url = f"https://www.avbase.net/works/{canonical_id}"
    data = await get_next_data(url)
    return data.get("props", {}).get("pageProps", {}).get("work", {})


# ---------------------------
# 解析 Work 数据为 MovieData
# ---------------------------
def parse_work_to_movie(work: dict) -> MovieData:
    min_date = parse_min_date(work.get("min_date"))
    return MovieData(
        work_id=work["work_id"],
        prefix=work.get("prefix", ""),
        title=work.get("title", ""),
        min_date=min_date,
        casts=[c["actor"] for c in work.get("casts", [])],
        actors=work.get("actors", []),
        tags=work.get("tags", []),
        genres=[g["name"] for g in work.get("genres", [])],
    )


def add_products_to_db(db, work_products: list[dict], movie_id: int):
    for p in work_products:
        min_date = parse_min_date(p.get("date"))
        product_data = dict(
            product_id=p["product_id"],
            url=p["url"],
            image_url=p.get("image_url"),
            title=p.get("title"),
            source=p.get("source"),
            thumbnail_url=p.get("thumbnail_url"),
            date=min_date,
            maker=p.get("maker", {}).get("name") if p.get("maker") else None,
            label=p.get("label", {}).get("name") if p.get("label") else None,
            series=p.get("series", {}).get("name") if p.get("series") else None,
            sample_image_urls=p.get("sample_image_urls", []),
            director=(
                p.get("iteminfo", {}).get("director") if p.get("iteminfo") else None
            ),
            price=p.get("iteminfo", {}).get("price") if p.get("iteminfo") else None,
            volume=p.get("iteminfo", {}).get("volume") if p.get("iteminfo") else None,
            work_id=movie_id,
        )
        db.add(MovieProduct(**product_data))

def merge_products(products: list[dict]) -> dict:
    merged = {}
    for p in products:
        for key, value in p.items():
            if value is not None and not (isinstance(value, list) and len(value) == 0):
                if key not in merged:
                    merged[key] = value
    return merged
