from .model import RankingType, FC2RankingItem, FC2VideoInformation
from .helper import parse_ranking
from utils.logs import LOG_ERROR, LOG_INFO

import asyncio

import random
import httpx


base_url = "https://adult.contents.fc2.com/ranking/article"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://adult.contents.fc2.com/",
    "Connection": "keep-alive",
}


async def get_ranking(
    page: int = 1,
    term: RankingType = RankingType.monthly,
    retries: int = 3,
) -> list[FC2RankingItem]:
    url = f"{base_url}/{term.value}?page={page}"

    async with httpx.AsyncClient(
        headers=headers,
        timeout=20,
        follow_redirects=True,
    ) as client:
        for attempt in range(1, retries + 1):
            try:
                await asyncio.sleep(random.uniform(1.2, 2.5))

                r = await client.get(url)
                r.raise_for_status()

                html = r.text
                result = parse_ranking(html, page, term)

                if result:
                    return result

                raise ValueError("Parsed empty ranking")

            except Exception as e:
                LOG_ERROR(
                    f"[FC2][HTTP] Attempt {attempt} failed "
                    f"(term={term.value}, page={page}): {e}"
                )
                if attempt < retries:
                    await asyncio.sleep(2)
                else:
                    return []


async def get_information_by_number(number: str) -> FC2VideoInformation:
    url = f"https://adult.contents.fc2.com/article/{number}/?lang=ja"

    async with httpx.AsyncClient(
        headers=headers,
        timeout=20,
        follow_redirects=True,
    ) as client:
        r = await client.get(url)
        r.raise_for_status()

        html = r.text

    from .helper import parse_information

    return parse_information(html)
