import json

from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from fastapi import HTTPException
from .model import SocialMedia, Movie
from core.config import _config

from core.system.model import DecryptedImagePayload
from core.system import encrypt_payload
import time


async def get_movies(url: str, changeImagePrefix: bool = True) -> List[Movie]:
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

                    image_payload = DecryptedImagePayload(
                        url=img_url, exp=int(time.time()) + _config.get("SYSTEM_IMAGE_EXPIRE_HOURS") * 3600, src="avbase"
                    )

                    image_token = encrypt_payload(image_payload)

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
    from core.playwright import _playwright_service

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
    from core.playwright import _playwright_service

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
