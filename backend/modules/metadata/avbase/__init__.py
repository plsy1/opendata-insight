import json
from bs4 import BeautifulSoup
from typing import List
from collections import defaultdict
from .model import *
from .helper import *
from core.config import _config
from core.system import replace_domain_in_value, encrypt_payload
from core.system.model import DecryptedImagePayload
import time


async def get_actress_info_by_actress_name(
    name: str, changeImagePrefix: bool = True
) -> Actress:
    actress = Actress(name=name)

    url = f"https://www.avbase.net/talents/{name}"
    content = await get_raw_html(url)

    soup = BeautifulSoup(content, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        data = json.loads(script_tag.string)
        page_props = data["props"]["pageProps"]
        talent = page_props.get("talent", {})

        primary = talent.get("primary", {})

        if changeImagePrefix:
            real_image_url = primary.get("image_url", "")
            SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")

            image_payload = DecryptedImagePayload(
                url=real_image_url, exp=int(time.time()) + _config.get("SYSTEM_IMAGE_EXPIRE_HOURS") * 3600, src="avbase"
            )

            image_token = encrypt_payload(image_payload)
            actress.avatar_url = f"{SYSTEM_IMAGE_PREFIX}{image_token}"
        else:
            actress.avatar_url = f'{primary.get("image_url")}'

        fanza = (primary.get("meta") or {}).get("fanza") or {}
        for k, v in fanza.items():
            if hasattr(actress, k):
                setattr(actress, k, v)

        actors = talent.get("actors", [])
        actress.aliases = [actor.get("name") for actor in actors if actor.get("name")]

    actress.social_media = get_social_media_links(soup)

    return actress


async def get_movie_info_by_actress_name(
    name: str, page: int, changeImagePrefix: bool = True
) -> List[Movie]:
    url = f"https://www.avbase.net/talents/{name}?q=&page={page}"
    return await get_movies(url, changeImagePrefix=changeImagePrefix)


async def get_movie_info_by_keywords(keywords: str, page: int) -> List[Movie]:
    url = f"https://www.avbase.net/works?q={keywords}&page={page}"
    return await get_movies(url)


async def get_actors_from_work(
    canonical_id: str, changeImagePrefix: bool = True
) -> MovieInformation:
    url = f"https://www.avbase.net/works/{canonical_id}"
    data = await get_next_data(url)

    work = data.get("props", {}).get("pageProps", {}).get("work", {})
    min_date_str = work.get("min_date", "")
    if min_date_str:
        work["min_date"] = date_trans(min_date_str)
        data["props"]["pageProps"]["work"]["min_date"] = work["min_date"]

    if changeImagePrefix:
        SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
        data = replace_domain_in_value(data, SYSTEM_IMAGE_PREFIX)

    movie_info = MovieInformation(**data)

    return movie_info


async def get_index():
    url = f"https://www.avbase.net"
    data = await get_next_data(url)
    data = data.get("props").get("pageProps")
    works = data.get("works")
    products = [p for work in works for p in work.get("products", [])]
    newbie_talents = data.get("newbie_talents")
    popular_talents = data.get("popular_talents")
    SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")
    newbie_talents = replace_domain_in_value(newbie_talents, SYSTEM_IMAGE_PREFIX)
    popular_talents = replace_domain_in_value(popular_talents, SYSTEM_IMAGE_PREFIX)

    seen_titles = set()
    unique_products = []
    for p in products:
        title = p.get("title")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)

        p = replace_domain_in_value(p, SYSTEM_IMAGE_PREFIX)
        unique_products.append(p)

    return {
        "products": unique_products,
        "newbie_talents": newbie_talents,
        "popular_talents": popular_talents,
    }


async def get_release_grouped_by_prefix(
    date_str: str,changeImagePrefix: bool = True
) -> List[AvbaseEverydayReleaseByPrefix]:
    """
    获取指定日期的作品列表，并按 prefix 分组
    date_str: 'YYYY-MM-DD'
    """
    SYSTEM_IMAGE_PREFIX = _config.get("SYSTEM_IMAGE_PREFIX")

    all_works = []

    page = 1
    while True:
        url = f"https://www.avbase.net/works/date/{date_str}?page={page}"
        data = await get_next_data(url)

        works_data = data.get("props", {}).get("pageProps", {}).get("works", [])

        if changeImagePrefix:
            works_data = replace_domain_in_value(works_data, SYSTEM_IMAGE_PREFIX)
        if not works_data:
            break

        all_works.extend(works_data)
        page += 1

    grouped: defaultdict[str, List[Work]] = defaultdict(list)

    for work_dict in all_works:
        products = work_dict.get("products", [])
        prefix = next(
            (
                p.get("maker", {}).get("name")
                for p in products
                if p.get("maker", {}).get("name")
            ),
            "Unknown",
        )

        try:
            work = Work(**work_dict)
            grouped[prefix].append(work)
        except Exception as e:
            continue

    groups_list: List[AvbaseEverydayReleaseByPrefix] = [
        AvbaseEverydayReleaseByPrefix(prefixName=prefix or "Unknown", works=works)
        for prefix, works in grouped.items()
    ]

    normal_groups = [g for g in groups_list if g.prefixName != "Unknown"]
    no_prefix_group = [g for g in groups_list if g.prefixName == "Unknown"]

    normal_groups_sorted = sorted(
        normal_groups, key=lambda x: len(x.works), reverse=True
    )

    result = normal_groups_sorted + no_prefix_group

    return result
