from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from core.auth import tokenInterceptor
from modules.notification.telegram.text import *
from modules.metadata.avbase import *
from services.feed import (
    actor_operation_service,
    movie_subscribe_list_service,
    movie_feed_service,
    actor_list_service,
)
from services.feed.model import *

router = APIRouter()


@router.post("/movieSubscribe")
async def add_movie_feed(
    keyword: str = Query(...),
    actors: str = Query(...),
    img: str = Query(...),
    link: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    ok = await movie_feed_service(
        MovieFeedOperation.ADD,
        keyword=keyword,
        actors=actors,
        img=img,
        link=link,
    )
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Add movie feed failed")


@router.delete("/movieSubscribe")
async def remove_movie_feed(
    actors: str = Query(...),
    keyword: str = Query(...),
    img: str = Query(...),
    link: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    ok = await movie_feed_service(
        MovieFeedOperation.REMOVE, keyword=keyword, actors=actors, img=img, link=link
    )
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Remove movie feed failed")


@router.get("/movieSubscribe")
async def get_movies_subscribe_list(
    isValid: str = Depends(tokenInterceptor),
):
    return movie_subscribe_list_service(MovieStatus.SUBSCRIBE, True)


@router.post("/actorSubscribe")
async def add_actor_subscribe(
    name: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    if await actor_operation_service(name, Operation.SUBSCRIBE):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.delete("/actorSubscribe")
async def del_actor_subscribe(
    name: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    if await actor_operation_service(name, Operation.UNSUBSCRIBE):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.get("/actorSubscribe")
async def get_actor_subscribe_list(
    isValid: str = Depends(tokenInterceptor),
):
    return actor_list_service(ActorListType.SUBSCRIBE, True)


@router.post("/actorCollect")
async def add_actor_collect(
    name: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    if await actor_operation_service(name, Operation.COLLECT):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Collect failed",
    )


@router.delete("/actorCollect")
async def del_actor_collect(
    name: str = Query(...),
    isValid: str = Depends(tokenInterceptor),
):
    if await actor_operation_service(name, Operation.UNCOLLECT):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.get("/actorCollect")
async def get_actor_collect_list(
    isValid: str = Depends(tokenInterceptor),
):
    return actor_list_service(ActorListType.COLLECT, True)


@router.get("/movieDownloaded")
async def get_movies_downloaded_list(
    isValid: str = Depends(tokenInterceptor),
):
    return movie_subscribe_list_service(MovieStatus.DOWNLOADED, True)
