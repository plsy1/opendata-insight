from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from modules.metadata.prowlarr import Prowlarr
from services.auth import tokenInterceptor
from config import _config

router = APIRouter()


def format_size(size_in_bytes: int) -> str:
    """
    将字节大小转换为更易读的格式（MB/GB）。

    :param size_in_bytes: 字节数
    :return: 转换后的大小字符串
    """
    if size_in_bytes >= 1_073_741_824:
        return f"{size_in_bytes / 1_073_741_824:.2f} GB"
    elif size_in_bytes >= 1_048_576:
        return f"{size_in_bytes / 1_048_576:.2f} MB"
    else:
        return f"{size_in_bytes} bytes"


@router.get("/search")
async def search(
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    isValid: str = Depends(tokenInterceptor),
):
    """
    搜索Prowlarr中的内容，并且要求已认证的用户访问。

    :param query: 搜索关键词
    :param page: 页码，默认为1
    :param page_size: 每页返回的结果数量，默认为10
    :param current_user: 当前已认证的用户，来自依赖项
    :return: 搜索结果的JSON响应
    """
    
    PROWLARR_URL = _config.get("PROWLARR_URL")
    PROWLARR_KEY = _config.get("PROWLARR_KEY")

    prowlarr = Prowlarr(PROWLARR_URL, PROWLARR_KEY)

    search_results = prowlarr.search(query=query, page=page, page_size=page_size)

    if search_results is None:
        raise HTTPException(status_code=500, detail="Prowlarr API请求失败")

    return JSONResponse(content=search_results)
