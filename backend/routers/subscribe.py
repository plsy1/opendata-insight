from fastapi import APIRouter, HTTPException, Query, Depends, Response, status
from services.subscribe import *
from database import get_db
from sqlalchemy.orm import Session
from services.system import replace_domain_in_value

router = APIRouter()


@router.post("/movieSubscribe")
async def add_movie_feed(
    work_id: str = Query(...),
    db: Session = Depends(get_db),
):

    ok = movie_subscribe_service(db, MovieFeedOperation.ADD, work_id=work_id)
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Add movie feed failed")


@router.delete("/movieSubscribe")
async def remove_movie_feed(
    work_id: str = Query(...),
    db: Session = Depends(get_db),
):

    ok = movie_subscribe_service(db, MovieFeedOperation.REMOVE, work_id=work_id)
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Remove movie feed failed")


@router.get("/movieSubscribe")
async def get_movies_subscribe_list(
    db: Session = Depends(get_db),
):
    return movie_subscribe_list_service(db, MovieStatus.SUBSCRIBE)


@router.post("/actorSubscribe")
async def add_actor_subscribe(
    name: str = Query(...),
    db: Session = Depends(get_db),
):
    if await actor_operation_service(db, name, Operation.SUBSCRIBE):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.delete("/actorSubscribe")
async def del_actor_subscribe(
    name: str = Query(...),
    db: Session = Depends(get_db),
):
    if await actor_operation_service(db, name, Operation.UNSUBSCRIBE):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.get("/actorSubscribe")
async def get_actor_subscribe_list(
    db: Session = Depends(get_db),
):
    result = actor_list_service(db, ActorListType.SUBSCRIBE)
    return replace_domain_in_value(result)


@router.post("/actorCollect")
async def add_actor_collect(
    name: str = Query(...),
    db: Session = Depends(get_db),
):
    if await actor_operation_service(db, name, Operation.COLLECT):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Collect failed",
    )


@router.delete("/actorCollect")
async def del_actor_collect(
    name: str = Query(...),
    db: Session = Depends(get_db),
):
    if await actor_operation_service(db, name, Operation.UNCOLLECT):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Subscribe failed",
    )


@router.get("/actorCollect")
async def get_actor_collect_list(
    db: Session = Depends(get_db),
):
    result = actor_list_service(db, ActorListType.COLLECT)
    return replace_domain_in_value(result)


@router.get("/movieDownloaded")
async def get_movies_downloaded_list(
    db: Session = Depends(get_db),
):
    result = movie_subscribe_list_service(db, MovieStatus.DOWNLOADED)
    return replace_domain_in_value(result)
