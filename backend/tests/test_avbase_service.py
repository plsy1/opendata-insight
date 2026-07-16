import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from services.avbase import _actor_cache_expired


class ActorCacheTests(unittest.TestCase):
    def test_missing_timestamp_is_expired(self):
        record = SimpleNamespace(avatar_url=None, updated_at=None)
        self.assertTrue(_actor_cache_expired(record, cache_hours=24))

    def test_fresh_record_is_not_expired(self):
        now = datetime(2026, 7, 17, 12, 0, 0)
        record = SimpleNamespace(
            avatar_url=None,
            updated_at=now - timedelta(hours=1),
        )
        self.assertFalse(
            _actor_cache_expired(record, now=now, cache_hours=24)
        )

    def test_old_record_is_expired(self):
        now = datetime(2026, 7, 17, 12, 0, 0)
        record = SimpleNamespace(
            avatar_url=None,
            updated_at=now - timedelta(hours=25),
        )
        self.assertTrue(_actor_cache_expired(record, now=now, cache_hours=24))


if __name__ == "__main__":
    unittest.main()
