from modules.scheduler import JobInfo
from apscheduler.triggers.interval import IntervalTrigger
import inspect
from fastapi.concurrency import run_in_threadpool
from utils.logs import LOG_ERROR
import asyncio


def list_jobs_service():
    from modules.scheduler import _scheduler_service

    if not _scheduler_service.scheduler:
        return []

    results = []
    for job in _scheduler_service.scheduler.get_jobs():
        is_interval = isinstance(job.trigger, IntervalTrigger)
        results.append(
            JobInfo(
                id=job.id,
                name=job.name,
                next_run_time=getattr(job, "next_run_time", None),
                trigger=str(job.trigger),
                schedule_type="interval" if is_interval else "other",
                interval_seconds=(
                    int(job.trigger.interval.total_seconds())
                    if is_interval
                    else None
                ),
            )
        )
    return results


async def run_job_service(job_id: str):
    from modules.scheduler import _scheduler_service

    if not _scheduler_service.scheduler:
        raise RuntimeError("Scheduler not initialized")

    job = _scheduler_service.scheduler.get_job(job_id)
    if not job:
        raise KeyError(f"Job {job_id} not found")

    async def _runner():
        try:
            if inspect.iscoroutinefunction(job.func):
                await job.func()
            else:
                await run_in_threadpool(job.func)
        except Exception as e:
            LOG_ERROR(f"Job {job_id} failed: {e}")

    asyncio.create_task(_runner())
