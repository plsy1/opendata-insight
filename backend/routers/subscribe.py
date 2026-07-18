from fastapi import APIRouter, HTTPException, Query, Depends, Response, status
from services.subscribe import *
from database import get_db
from sqlalchemy.orm import Session
from services.system import replace_domain_in_value
from schemas.actor import ActorListOut, ActorOrderUpdate
from schemas.feed import (
    MovieFeedItemOut,
    MovieFeedPageOut,
    MovieSubscriptionRulesUpdate,
)

router = APIRouter()


@router.post("/movieSubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def add_movie_feed(
    work_id: str = Query(...),
    db: Session = Depends(get_db),
):

    ok = movie_subscribe_service(db, MovieFeedOperation.ADD, work_id=work_id)
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Add movie feed failed")


@router.delete("/movieSubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def remove_movie_feed(
    work_id: str = Query(...),
    db: Session = Depends(get_db),
):

    ok = movie_subscribe_service(db, MovieFeedOperation.REMOVE, work_id=work_id)
    if ok:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(500, "Remove movie feed failed")


@router.get("/movieSubscribe", response_model=list[MovieFeedItemOut])
async def get_movies_subscribe_list(
    db: Session = Depends(get_db),
):
    result = movie_subscribe_list_service(db, MovieStatus.SUBSCRIBE)
    return replace_domain_in_value(result)


@router.put(
    "/movieSubscribe/rules",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def update_movie_subscription_rules(
    rules: MovieSubscriptionRulesUpdate,
    work_id: str = Query(...),
    db: Session = Depends(get_db),
):
    if update_movie_subscription_rules_service(db, work_id, rules):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Movie subscription not found",
    )


@router.post("/actorSubscribe", status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/actorSubscribe", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/actorSubscribe", response_model=list[ActorListOut])
async def get_actor_subscribe_list(
    db: Session = Depends(get_db),
):
    result = actor_list_service(db, ActorListType.SUBSCRIBE)
    return replace_domain_in_value(result)


@router.post("/actorCollect", status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/actorCollect", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/actorCollect", response_model=list[ActorListOut])
async def get_actor_collect_list(
    db: Session = Depends(get_db),
):
    result = actor_list_service(db, ActorListType.COLLECT)
    return replace_domain_in_value(result)


@router.put("/actorOrder", status_code=status.HTTP_204_NO_CONTENT)
async def update_actor_order(
    data: ActorOrderUpdate,
    db: Session = Depends(get_db),
):
    try:
        order_type = ActorListType(data.type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order type")

    if update_actor_order_service(db, order_type, data.names):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Update order failed",
    )


@router.get("/movieDownloaded", response_model=MovieFeedPageOut)
async def get_movies_downloaded_list(
    limit: int = Query(30, ge=1, le=100),
    cursor: str | None = Query(None),
    db: Session = Depends(get_db),
):
    try:
        result = movie_downloaded_page_service(
            db,
            limit=limit,
            cursor=cursor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return replace_domain_in_value(result)
