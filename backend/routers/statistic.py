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


@router.get("/all", response_model=StatAllOut)
def api_stat_all(db: Session = Depends(get_db)):
    return {
        "overview": stat_overview(db),
        "daily": stat_daily_subscribe(db),
        "studio": stat_workid_prefix(db, 10),
        "actors": stat_actors_subscribed(db, 10),
    }
