from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from utils.logs import LOG_INFO, LOG_ERROR
from .jobs import *
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import asyncio
import os


@dataclass
class JobInfo:
    id: str
    name: str
    next_run_time: Optional[datetime]
    trigger: str


class AppScheduler:
    def __init__(self):
        self.scheduler: AsyncIOScheduler | None = None
        self._job_counter = 0

    def job_listener(self, event):
        if event.exception:
            LOG_ERROR(f"Job {event.job_id} failed: {event.exception}")
        else:
            LOG_INFO(f"Job {event.job_id} completed")

    async def init(self):
        if self.scheduler is not None:
            return
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_listener(
            self.job_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR,
        )
        self.scheduler.start()
        if os.environ.get("UVICORN_RUN_MAIN") == "true":
            LOG_INFO("Scheduler started")

    def add_job(self, func, trigger=None, job_id=None, name=None, **trigger_args):
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        if job_id is None:
            self._job_counter += 1
            job_id = f"{self._job_counter}"

        trigger_instance = (
            trigger(**trigger_args) if trigger else IntervalTrigger(seconds=60)
        )
        self.scheduler.add_job(func, trigger_instance, id=job_id, name=name or job_id)
        return job_id

    def remove_job(self, job_id):
        if self.scheduler:
            self.scheduler.remove_job(job_id)
            LOG_INFO(f"Removed job: {job_id}")

    async def shutdown(self):
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            LOG_INFO("Scheduler shutdown")


_scheduler_service: AppScheduler | None = None
_init_lock = asyncio.Lock()


async def init_scheduler_service() -> AppScheduler:
    global _scheduler_service
    async with _init_lock:
        if _scheduler_service is None:
            _scheduler_service = AppScheduler()
            await _scheduler_service.init()

            _scheduler_service.add_job(
                update_emby_movies_in_db,
                trigger=IntervalTrigger,
                name="update emby",
                hours=1,
            )
            _scheduler_service.add_job(
                clean_cache_dir,
                trigger=IntervalTrigger,
                name="clean image cache",
                hours=3,
            )
            _scheduler_service.add_job(
                refresh_feeds,
                trigger=IntervalTrigger,
                name="refresh subscribe",
                hours=7,
            )
            _scheduler_service.add_job(
                update_avbase_release_everyday,
                trigger=IntervalTrigger,
                name="update avbase release everyday",
                hours=7,
            )
            _scheduler_service.add_job(
                update_avbase_index_actor_service,
                trigger=IntervalTrigger,
                name="update_avbase_index_actor_service",
                hours=12,
            )
            _scheduler_service.add_job(
                update_fc2_ranking,
                trigger=IntervalTrigger,
                name="update fc2 ranking",
                hours=3,
            )
            _scheduler_service.add_job(
                update_actor_data_periodic,
                trigger=IntervalTrigger,
                name="update actor data periodic",
                hours=24,
            )
            
            LOG_INFO("AppScheduler initialized with default jobs")
    return _scheduler_service


async def shutdown_scheduler_service():
    global _scheduler_service
    if _scheduler_service:
        await _scheduler_service.shutdown()
        _scheduler_service = None
