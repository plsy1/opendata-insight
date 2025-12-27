from fastapi import APIRouter, Depends
from modules.statistic import *
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/overview")
def api_stat_overview(db: Session = Depends(get_db)):
    return stat_overview(db)


@router.get("/daily")
def api_stat_daily(db: Session = Depends(get_db)):
    return stat_daily(db)


@router.get("/studio")
def api_stat_studio(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return stat_studio(db, limit)


@router.get("/actors")
def api_stat_actors(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return stat_actors(db, limit)


@router.get("/all")
def api_stat_all(db: Session = Depends(get_db)):
    return {
        "overview": stat_overview(db),
        "daily": stat_daily(db),
        "studio": stat_studio(db, 10),
        "actors": stat_actors(db, 10),
    }