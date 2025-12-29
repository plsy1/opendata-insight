from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from services.auth import tokenInterceptor

router = APIRouter()


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

    from modules.metadata.prowlarr import _prowlarr_instance

    search_results = await _prowlarr_instance.search(
        query=query, page=page, page_size=page_size
    )

    if search_results is None:
        raise HTTPException(status_code=500, detail="Prowlarr API请求失败")

    return JSONResponse(content=search_results)
