from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from utils.logs import LOG_INFO, LOG_ERROR
from .jobs import *
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import asyncio
import inspect
import os


@dataclass
class JobInfo:
    id: str
    name: str
    next_run_time: Optional[datetime]
    trigger: str
    schedule_type: str
    interval_seconds: Optional[int]
    is_running: bool = False


class AppScheduler:
    def __init__(self):
        self.scheduler: AsyncIOScheduler | None = None
        self._job_counter = 0
        self._job_functions: dict[str, object] = {}
        self._running_job_ids: set[str] = set()
        self._manual_tasks: set[asyncio.Task] = set()

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
        self._job_functions[job_id] = func

        async def guarded_job():
            started = await self.execute_job(job_id)
            if not started:
                LOG_INFO(f"Skipped already-running job: {job_id}")

        self.scheduler.add_job(
            guarded_job,
            trigger_instance,
            id=job_id,
            name=name or job_id,
        )
        return job_id

    def is_job_running(self, job_id: str) -> bool:
        return job_id in self._running_job_ids

    def _reserve_job(self, job_id: str) -> bool:
        if job_id in self._running_job_ids:
            return False
        if job_id not in self._job_functions:
            raise KeyError(f"Job {job_id} not found")
        self._running_job_ids.add(job_id)
        return True

    async def _execute_reserved_job(self, job_id: str) -> None:
        try:
            func = self._job_functions[job_id]
            if inspect.iscoroutinefunction(func):
                await func()
            else:
                await asyncio.to_thread(func)
        finally:
            self._running_job_ids.discard(job_id)

    async def execute_job(self, job_id: str) -> bool:
        if not self._reserve_job(job_id):
            return False
        await self._execute_reserved_job(job_id)
        return True

    def queue_job(self, job_id: str) -> bool:
        if not self._reserve_job(job_id):
            return False

        async def runner():
            try:
                await self._execute_reserved_job(job_id)
            except Exception as exc:
                LOG_ERROR(f"Job {job_id} failed: {exc}")

        task = asyncio.create_task(runner())
        self._manual_tasks.add(task)
        task.add_done_callback(self._manual_tasks.discard)
        return True

    def remove_job(self, job_id):
        if self.scheduler:
            self.scheduler.remove_job(job_id)
            self._job_functions.pop(job_id, None)
            LOG_INFO(f"Removed job: {job_id}")

    async def shutdown(self):
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            for task in self._manual_tasks:
                task.cancel()
            if self._manual_tasks:
                await asyncio.gather(
                    *self._manual_tasks,
                    return_exceptions=True,
                )
            self._manual_tasks.clear()
            self._running_job_ids.clear()
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
                job_id="sync_emby_library",
                name="Sync Emby library",
                hours=1,
            )
            _scheduler_service.add_job(
                clean_cache_dir,
                trigger=IntervalTrigger,
                job_id="clean_image_cache",
                name="Clean image cache",
                hours=3,
            )
            _scheduler_service.add_job(
                refresh_feeds,
                trigger=IntervalTrigger,
                job_id="refresh_subscriptions",
                name="Refresh subscriptions",
                hours=7,
            )
            _scheduler_service.add_job(
                update_avbase_release_everyday,
                trigger=IntervalTrigger,
                job_id="sync_avbase_releases",
                name="Sync AVBase releases",
                hours=7,
            )
            _scheduler_service.add_job(
                update_avbase_index_actor_service,
                trigger=IntervalTrigger,
                job_id="sync_avbase_performers",
                name="Sync AVBase performers",
                hours=12,
            )
            _scheduler_service.add_job(
                update_fc2_ranking,
                trigger=IntervalTrigger,
                job_id="sync_fc2_rankings",
                name="Sync FC2 rankings",
                hours=3,
            )
            _scheduler_service.add_job(
                update_actor_data_periodic,
                trigger=IntervalTrigger,
                job_id="refresh_performer_profiles",
                name="Refresh performer profiles",
                hours=24,
            )
            
            LOG_INFO("AppScheduler initialized with default jobs")
    return _scheduler_service


async def shutdown_scheduler_service():
    global _scheduler_service
    if _scheduler_service:
        await _scheduler_service.shutdown()
        _scheduler_service = None
