from fastapi import APIRouter, Depends
from services.statistic import *
from database import get_db
from sqlalchemy.orm import Session
from schemas.statistic import (
    StatActorOut,
    StatAllOut,
    StatDailyOut,
    StatOverviewOut,
    StatStudioOut,
    StatNamedCountOut,
)

router = APIRouter()


@router.get("/overview", response_model=StatOverviewOut)
def api_stat_overview(db: Session = Depends(get_db)):
    return stat_overview(db)


@router.get("/daily", response_model=list[StatDailyOut])
def api_stat_daily(db: Session = Depends(get_db)):
    return stat_daily_subscribe(db)


@router.get("/studio", response_model=list[StatStudioOut])
def api_stat_studio(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return stat_workid_prefix(db, limit)


@router.get("/actors", response_model=list[StatActorOut])
def api_stat_actors(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return stat_actors_subscribed(db, limit)


@router.get("/makers", response_model=list[StatNamedCountOut])
def api_stat_makers(limit: int = 10, db: Session = Depends(get_db)):
    return stat_makers(db, limit)


@router.get("/labels", response_model=list[StatNamedCountOut])
def api_stat_labels(limit: int = 10, db: Session = Depends(get_db)):
    return stat_labels(db, limit)


@router.get("/series", response_model=list[StatNamedCountOut])
def api_stat_series(limit: int = 10, db: Session = Depends(get_db)):
    return stat_series(db, limit)


@router.get("/taxonomy", response_model=list[StatNamedCountOut])
def api_stat_taxonomy(limit: int = 10, db: Session = Depends(get_db)):
    return stat_taxonomy(db, limit)


@router.get("/genres", response_model=list[StatNamedCountOut])
def api_stat_genres(limit: int = 10, db: Session = Depends(get_db)):
    return stat_genres(db, limit)


@router.get("/tags", response_model=list[StatNamedCountOut])
def api_stat_tags(limit: int = 10, db: Session = Depends(get_db)):
    return stat_tags(db, limit)


@router.get("/all", response_model=StatAllOut)
def api_stat_all(db: Session = Depends(get_db)):
    product_metadata = stat_product_metadata(db, 10)
    taxonomy_metadata = stat_taxonomy_metadata(db, 10)
    return {
        "overview": stat_overview(db),
        "daily": stat_daily_subscribe(db),
        "studio": stat_workid_prefix(db, 10),
        "actors": stat_actors_subscribed(db, 10),
        **product_metadata,
        **taxonomy_metadata,
    }
