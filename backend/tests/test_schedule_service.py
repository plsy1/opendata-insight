import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from apscheduler.triggers.interval import IntervalTrigger

from services.schedule import list_jobs_service


class ScheduleServiceTests(unittest.TestCase):
    def test_interval_job_has_structured_schedule_fields(self):
        job = SimpleNamespace(
            id="clean_image_cache",
            name="Clean image cache",
            next_run_time=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
            trigger=IntervalTrigger(hours=3),
        )
        scheduler = SimpleNamespace(get_jobs=lambda: [job])

        with patch(
            "modules.scheduler._scheduler_service",
            SimpleNamespace(
                scheduler=scheduler,
                is_job_running=lambda _job_id: False,
            ),
        ):
            result = list_jobs_service()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].schedule_type, "interval")
        self.assertEqual(result[0].interval_seconds, 10800)
        self.assertEqual(result[0].id, "clean_image_cache")
        self.assertFalse(result[0].is_running)


if __name__ == "__main__":
    unittest.main()
