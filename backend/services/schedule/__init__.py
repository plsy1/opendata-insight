from modules.scheduler import JobInfo
from apscheduler.triggers.interval import IntervalTrigger


class JobAlreadyRunningError(RuntimeError):
    pass


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
                is_running=_scheduler_service.is_job_running(job.id),
            )
        )
    return results


async def run_job_service(job_id: str):
    from modules.scheduler import _scheduler_service

    if not _scheduler_service.scheduler:
        raise RuntimeError("Scheduler not initialized")

    if not _scheduler_service.scheduler.get_job(job_id):
        raise KeyError(f"Job {job_id} not found")
    if not _scheduler_service.queue_job(job_id):
        raise JobAlreadyRunningError(f"Job {job_id} is already running")
