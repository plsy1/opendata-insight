from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .model import FC2RankingItem, FC2VideoInformation, RankingType


def parse_int(text: str) -> int:
    import re

    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


FC2_BASE = "https://adult.contents.fc2.com"


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

        owner_tag = item.select_one(".c-ranklist-110_own a:last-of-type")
        owner = owner_tag.get_text(strip=True) if owner_tag else None

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

        author_link = header_info.find("a", href=lambda x: x and "author_id" in x)
        if author_link:
            info.author = author_link.get_text(strip=True)

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
