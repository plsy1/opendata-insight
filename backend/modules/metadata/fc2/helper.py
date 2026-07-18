from bs4 import BeautifulSoup
import re
from urllib.parse import parse_qs, urljoin, urlparse

from .model import (
    FC2RankingItem,
    FC2SellerInformation,
    FC2SellerWork,
    FC2SellerWorksPage,
    FC2VideoInformation,
    RankingType,
)


def parse_int(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


FC2_BASE = "https://adult.contents.fc2.com"


def _absolute_url(value: str | None) -> str:
    if not value:
        return ""
    if value.startswith("//"):
        return f"https:{value}"
    return urljoin(FC2_BASE, value)


def _seller_id_from_url(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"/users/([^/?#]+)/?", value)
    return match.group(1) if match else None


def parse_ranking(
    html: str, page: int = 1, term: RankingType = RankingType.monthly
) -> list[FC2RankingItem]:
    soup = BeautifulSoup(html, "lxml")

    rank_box = soup.find("div", class_="c-rankbox-100")
    if not rank_box:
        return []

    items = rank_box.find_all("div", class_="c-ranklist-110", recursive=False)
    results: list[FC2RankingItem] = []

    for index, item in enumerate(items, start=1):
        rank = (page - 1) * len(items) + index

        title_tag = item.select_one("h3 a")
        title = title_tag.get_text(strip=True) if title_tag else ""
        link = urljoin(FC2_BASE, title_tag["href"]) if title_tag else ""

        article_id = link.split("id=")[-1] if "id=" in link else ""

        img_tag = item.select_one(".c-ranklist-110_tmb img")
        cover = ""
        if img_tag:
            cover = img_tag.get("data-src") or img_tag.get("src") or ""
            if cover.startswith("//"):
                cover = "https:" + cover

        owner_tag = item.select_one(
            '.c-ranklist-110_own > a[href*="/users/"]'
        ) or item.select_one('.c-ranklist-110_own a[href*="/users/"]')
        owner = owner_tag.get_text(strip=True) if owner_tag else None
        seller_id = _seller_id_from_url(owner_tag.get("href") if owner_tag else None)

        rating_tag = item.select_one("ul.c-rankstar-110 li.c-rankstar-110_num")
        rating = parse_int(rating_tag.get_text(strip=True)) if rating_tag else 0

        comment_tag = item.select_one("ul.c-rankcmt-110 li.c-rankstar-110_num")
        comment_count = (
            parse_int(comment_tag.get_text(strip=True)) if comment_tag else 0
        )

        comments = [
            c.get_text(strip=True)
            for c in item.select(".c-rankcmt-120_comment")
            if c.get_text(strip=True)
        ]

        results.append(
            FC2RankingItem(
                term=term.value,
                page=page,
                rank=rank,
                article_id=article_id,
                title=title,
                url=link,
                cover=cover,
                owner=owner,
                seller_id=seller_id,
                rating=rating,
                comment_count=comment_count,
                hot_comments=comments,
            )
        )

    return results


def parse_information(html: str) -> FC2VideoInformation:
    soup = BeautifulSoup(html, "lxml")
    info = FC2VideoInformation()

    meta_img = soup.find("meta", property="og:image")
    if meta_img and meta_img.has_attr("content"):
        info.cover = meta_img["content"].strip()

    p_tag = soup.find("p", class_="items_article_info")
    if p_tag:
        info.duration = p_tag.get_text(strip=True)

    header_info = soup.find("div", class_="items_article_headerInfo")
    if header_info:
        title = header_info.find("h3")
        if title:
            info.title = title.get_text(strip=True)

        author_link = header_info.select_one('a[href*="/users/"]')
        if author_link:
            info.author = author_link.get_text(strip=True)
            info.seller_id = _seller_id_from_url(author_link.get("href"))

    soft_devices = soup.find_all("div", class_="items_article_softDevice")
    for div in soft_devices:
        text = div.get_text(strip=True)
        if text.startswith("販売日") or text.startswith("Sale Day"):
            info.sale_day = text.split(":")[-1].strip()

        if text.startswith("商品ID") or text.startswith("Product ID"):
            product_id = text.split(":")[-1].strip().replace(" ", "-")
            info.product_id = product_id
            info.article_id = product_id.split("-")[-1]

    sectionSampleImages = soup.find("section", class_="items_article_SampleImages")
    if sectionSampleImages:
        ul = sectionSampleImages.find("ul", class_="items_article_SampleImagesArea")
        if ul:
            for li in ul.find_all("li"):
                a_tag = li.find("a")
                if a_tag and a_tag.has_attr("href"):
                    href = a_tag["href"].strip()
                    if href.startswith("//"):
                        href = "https:" + href
                    info.sample_images.append(href)

    return info


def parse_seller_information(html: str, seller_id: str) -> FC2SellerInformation:
    soup = BeautifulSoup(html, "lxml")

    author_node = soup.find("script", attrs={"data-authorid": True})
    author_id = author_node.get("data-authorid", "").strip() if author_node else ""
    account = soup.select_one(".seller_user_account")
    name_node = account.select_one("[data-accountname]") if account else None
    icon_node = (
        account.select_one('.seller_user_accountIcon img[data-image="accountIcon"]')
        if account
        else None
    )
    name = (
        name_node.get_text(strip=True)
        if name_node
        else (icon_node.get("alt", "").strip() if icon_node else "")
    )

    if not author_id or not name:
        raise ValueError("FC2 seller profile is unavailable")

    banner_node = soup.select_one("img[data-mainvisual]")
    short_intro_node = account.select_one('[data-label="short_intro"]') if account else None
    description_node = account.select_one(".seller_user_accountExp p") if account else None

    product_count = 0
    follower_count = 0
    if account:
        for node in account.select(".seller_user_accountInfo > p span"):
            text = node.get_text(" ", strip=True)
            if "商品" in text or "Product" in text:
                product_count = parse_int(text)
            elif "フォロワー" in text or "Follower" in text:
                follower_count = parse_int(text)

    return FC2SellerInformation(
        seller_id=seller_id,
        author_id=author_id,
        name=name,
        profile_url=f"{FC2_BASE}/users/{seller_id}/",
        avatar_url=_absolute_url(icon_node.get("src") if icon_node else None) or None,
        banner_url=_absolute_url(banner_node.get("src") if banner_node else None) or None,
        short_intro=short_intro_node.get_text(" ", strip=True) if short_intro_node else None,
        description=description_node.get_text(" ", strip=True) if description_node else None,
        product_count=product_count,
        follower_count=follower_count,
    )


def parse_seller_works(
    html: str,
    seller_id: str,
    page: int = 1,
) -> FC2SellerWorksPage:
    soup = BeautifulSoup(html, "lxml")
    works: list[FC2SellerWork] = []

    for card in soup.select("section.search_cntFlexWp > div.c-cntCard-110-f"):
        seller_link = card.select_one(".c-cntCard-110-f_seller a")
        card_seller_id = _seller_id_from_url(
            seller_link.get("href") if seller_link else None
        )

        # FC2 mixes sponsored works from other sellers into search results.
        if card_seller_id != seller_id:
            continue

        title_link = card.select_one("a.c-cntCard-110-f_itemName")
        if not title_link:
            continue

        url = _absolute_url(title_link.get("href"))
        article_match = re.search(r"/article/(\d+)/?", url)
        if not article_match:
            continue

        image = card.select_one(".c-cntCard-110-f_thumb img")
        duration_node = card.select_one(".c-cntCard-110-f_thumb_num")
        description_node = card.select_one(".c-cntCard-110-f_itemScript")
        price_node = card.select_one(".c-cntCard-110-f_price")
        rating_node = card.select_one(".c-cntCard-110-f_recom")
        comment_node = card.select_one(".c-cntCard-110-f_comment")
        favorite_node = card.select_one(".c-cntCard-110-f_heart")

        works.append(
            FC2SellerWork(
                article_id=article_match.group(1),
                title=title_link.get("title") or title_link.get_text(" ", strip=True),
                url=url,
                cover=_absolute_url(
                    image.get("data-src") or image.get("src") if image else None
                )
                or None,
                duration=duration_node.get_text(strip=True) if duration_node else None,
                description=(
                    description_node.get_text(" ", strip=True)
                    if description_node
                    else None
                ),
                price=price_node.get_text(" ", strip=True) if price_node else None,
                rating=parse_int(rating_node.get_text(strip=True)) if rating_node else 0,
                comment_count=(
                    parse_int(comment_node.get_text(strip=True)) if comment_node else 0
                ),
                favorite_count=(
                    parse_int(favorite_node.get_text(strip=True)) if favorite_node else 0
                ),
                seller_id=card_seller_id,
                seller_name=seller_link.get_text(strip=True) if seller_link else None,
            )
        )

    total = 0
    total_node = soup.select_one(".search_header p")
    if total_node:
        total = parse_int(total_node.get_text(" ", strip=True))

    has_next = False
    for link in soup.select("a.items[href]"):
        query_page = parse_qs(urlparse(link.get("href", "")).query).get("page", [])
        if query_page and parse_int(query_page[0]) == page + 1:
            has_next = True
            break

    return FC2SellerWorksPage(
        works=works,
        page=page,
        total=total,
        has_next=has_next,
    )
