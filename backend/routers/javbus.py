from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import requests

router = APIRouter()


@router.get("/byActressNumber")
async def search(filter_value: str, page: int):
    """
    搜索并格式化返回的数据内容。

    :param filter_value: 搜索条件（例如明星名称）
    :param page: 页码，默认为1
    :param page_size: 每页返回的结果数量，默认为10
    :return: 搜索结果的JSON响应
    """
    url = "http://192.168.0.36:3000/api/movies"
    params = {
        "filterType": "star",
        "filterValue": filter_value,
        "magnet": "all",
        "page": page,
    }

    try:
        response = requests.get(
            url, params=params, headers={"accept": "application/json"}
        )
        response.raise_for_status()

        response_data = response.json()

        movies = response_data.get("movies", [])
        if not movies:
            raise HTTPException(status_code=404, detail="没有找到相关的电影数据")

        for movie in movies:
            movie_id = movie.get("id", "")
            movie_id = movie_id.lower().replace("-", "")
            movie["img"] = (
                f"https://pics.dmm.co.jp/mono/movie/adult/{movie_id}/{movie_id}pl.jpg"
            )
        return JSONResponse(content=movies)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 请求失败: {e}")


@router.get("/byKeyword")
async def search_by_keyword(keyword: str, videoType: str, page: int):
    """
    根据关键词搜索并格式化返回的数据内容。

    :param keyword: 搜索关键词（例如电影名称）
    :return: 搜索结果的JSON响应
    """
    url = "http://192.168.0.36:3000/api/movies/search"
    params = {"keyword": keyword, "magnet": "all", "type": videoType, "page": page}

    try:
        response = requests.get(
            url, params=params, headers={"accept": "application/json"}
        )
        response.raise_for_status()

        response_data = response.json()

        movies = response_data.get("movies", [])
        if not movies:
            raise HTTPException(status_code=404, detail="没有找到相关的电影数据")

        for movie in movies:
            movie_id = movie.get("id", "")
            movie_id = movie_id.lower().replace("-", "")
            movie["img_url"] = (
                f"https://pics.dmm.co.jp/mono/movie/adult/{movie_id}/{movie_id}pl.jpg"
            )

        return JSONResponse(content=movies)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 请求失败: {e}")
