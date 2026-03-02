import re, httpx
from typing import Optional
from .model import Actress, Work, RankingType

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "fanza-device": "BROWSER",
    "Origin": "https://video.dmm.co.jp",
    "Referer": "https://video.dmm.co.jp/",
    "Accept-Language": "ja,en;q=0.9",
}

GRAPHQL_URL = "https://api.video.dmm.co.jp/graphql"

async def fetch_actress_ranking(page: int) -> list[Actress]:
    query = """
    query ActressRankingPage($limit: Int!, $offset: Int, $filter: PPVActressRankingFilterInput!) {
      ppvActressRanking(limit: $limit, offset: $offset, filter: $filter) {
        items {
          id
          rank
          actress {
            id
            name
            imageUrl
            contentsCountOnSale
            latestContent {
              id
              title
              ... on PPVContentSummary {
                releaseStatus
                __typename
              }
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """
    
    # We fetch 100 at a time, but to support the existing page parameter we offset our request.
    page_size = 20
    offset = (page - 1) * page_size
    
    payload = {
        "operationName": "ActressRankingPage",
        "variables": {
            "filter": RankingType.monthly.graphql_filter(),
            "limit": page_size,
            "offset": offset
        },
        "query": query
    }

    async with httpx.AsyncClient(headers=HEADERS) as client:
        res = await client.post(GRAPHQL_URL, json=payload)
        res_data = res.json()
        
        if "errors" in res_data:
            print(f"FANZA GraphQL Error (Actress): {res_data['errors']}")
            
        actresses: list[Actress] = []
        
        data = res_data.get("data")
        if not data:
            return actresses
            
        items = data.get("ppvActressRanking", {}).get("items", [])
        for item in items:
            rank = str(item.get("rank"))
            actress_data = item.get("actress", {})
            name = actress_data.get("name")
            image = actress_data.get("imageUrl")
            profile_url = f"https://video.dmm.co.jp/av/list/?actress={actress_data.get('id')}" if actress_data.get("id") else None
            work_count = actress_data.get("contentsCountOnSale", 0)
            
            latest = actress_data.get("latestContent", {})
            latest_work = latest.get("title") if latest else None
            latest_work_url = f"https://video.dmm.co.jp/av/content/?id={latest.get('id')}" if latest and latest.get("id") else None
            
            actresses.append(
                Actress(
                    rank=rank,
                    name=name,
                    image=image,
                    profile_url=profile_url,
                    latest_work=latest_work,
                    latest_work_url=latest_work_url,
                    work_count=work_count,
                )
            )

        return actresses


async def fetch_movie_ranking(
    page: int = 1, term: RankingType = RankingType.monthly
) -> list[Work]:
    query = """
    query ContentRankingPage($limit: Int!, $offset: Int!, $filter: PPVContentRankingFilterInput) {
      ppvContentRanking(limit: $limit, offset: $offset, filter: $filter) {
        items {
          id
          rank
          content {
            title
            packageImage {
              largeUrl
              __typename
            }
            actresses {
              id
              name
              __typename
            }
            maker {
              id
              name
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """
    
    page_size = 20
    offset = (page - 1) * page_size
    
    payload = {
        "operationName": "ContentRankingPage",
        "variables": {
            "filter": term.graphql_filter(),
            "limit": page_size,
            "offset": offset
        },
        "query": query
    }

    async with httpx.AsyncClient(headers=HEADERS) as client:
        res = await client.post(GRAPHQL_URL, json=payload)
        res_data = res.json()
        
        if "errors" in res_data:
            print(f"FANZA GraphQL Error (Movie): {res_data['errors']}")
            
        results: list[Work] = []
        
        data = res_data.get("data")
        if not data:
            return results
            
        items = data.get("ppvContentRanking", {}).get("items", [])
        for item in items:
            rank = str(item.get("rank"))
            content = item.get("content", {})
            
            product_id = item.get("id")
            title = content.get("title")
            
            # The title often includes 【something】, we strip it just like before
            if title:
                title = re.sub(r"【.*?】", "", title).strip()
            
            # The large image URL is provided directly
            package_image = content.get("packageImage", {})
            image = package_image.get("largeUrl") if package_image else None
            
            # Extract the raw number from the image URL or the ID
            number = None
            if image:
                match = re.search(r"/([a-z]+\d+)/\1pl\.jpg$", image)
                number = match.group(1) if match else product_id
            else:
                number = product_id
                
            detail_url = f"https://video.dmm.co.jp/av/content/?id={product_id}" if product_id else None
            
            maker_data = content.get("maker")
            maker = maker_data.get("name") if maker_data else None
            
            actresses_data = content.get("actresses", [])
            actresses_list = [a.get("name") for a in actresses_data if a.get("name")]
            
            results.append(
                Work(
                    rank=rank,
                    title=title,
                    number=number,
                    image=image,
                    detail_url=detail_url,
                    maker=maker,
                    actresses=actresses_list,
                )
            )

        return results
