import asyncio
import unittest

from apscheduler.triggers.interval import IntervalTrigger

from modules.scheduler import AppScheduler


class SchedulerStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_running_job_cannot_be_queued_twice(self):
        scheduler = AppScheduler()
        await scheduler.init()
        started = asyncio.Event()
        release = asyncio.Event()

        async def job():
            started.set()
            await release.wait()

        scheduler.add_job(
            job,
            trigger=IntervalTrigger,
            job_id="test_job",
            hours=1,
        )

        try:
            self.assertTrue(scheduler.queue_job("test_job"))
            await asyncio.wait_for(started.wait(), timeout=1)

            self.assertTrue(scheduler.is_job_running("test_job"))
            self.assertFalse(scheduler.queue_job("test_job"))
            self.assertFalse(await scheduler.execute_job("test_job"))

            release.set()
            for _ in range(20):
                if not scheduler.is_job_running("test_job"):
                    break
                await asyncio.sleep(0)

            self.assertFalse(scheduler.is_job_running("test_job"))
        finally:
            release.set()
            await scheduler.shutdown()


if __name__ == "__main__":
    unittest.main()
