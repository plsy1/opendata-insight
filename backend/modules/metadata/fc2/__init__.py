from .model import RankingType, FC2RankingItem, FC2VideoInformation
from .helper import parse_ranking
from core.logs import LOG_ERROR

import asyncio

base_url = "https://adult.contents.fc2.com/ranking/article"


async def get_ranking(
    page: int = 1, term: RankingType = RankingType.monthly, retries: int = 3
) -> list[FC2RankingItem]:
    from core.playwright import _playwright_service

    context = await _playwright_service.get_context()
    pw_page = await context.new_page()

    try:
        url = f"{base_url}/{term.value}?page={page}"
        attempt = 0
        while attempt < retries:
            try:
                await pw_page.goto(url, timeout=10000)
                await pw_page.wait_for_selector("div.c-rankbox-100", timeout=10000)
                html = await pw_page.content()
                result = parse_ranking(html, page, term)
                if result:
                    return result
                else:
                    raise ValueError("Parsed empty result")
            except Exception as e:
                attempt += 1
                LOG_ERROR(f"Attempt {attempt} failed to load page {url}: {e}")
                if attempt < retries:
                    await asyncio.sleep(2)
                else:
                    return []
    finally:
        await pw_page.close()


async def get_information_by_number(number: str) -> FC2VideoInformation:
    from core.playwright import _playwright_service

    context = await _playwright_service.get_context()
    pw_page = await context.new_page()

    try:
        url = f"https://adult.contents.fc2.com/article/{number}/?lang=ja"
        await pw_page.goto(url, timeout=10000)
        await pw_page.wait_for_load_state("networkidle", timeout=10000)
        html = await pw_page.content()

        from .helper import parse_information

        info = parse_information(html)
        return info
    finally:
        await pw_page.close()
