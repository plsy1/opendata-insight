import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

import routers.avbase as avbase_router


class AvbaseRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_upstream_http_status_is_preserved(self):
        upstream_error = HTTPException(status_code=502, detail="upstream")
        with patch.object(
            avbase_router,
            "get_movie_list_by_actor_name_service",
            AsyncMock(side_effect=upstream_error),
        ):
            with self.assertRaises(HTTPException) as raised:
                await avbase_router.get_movie_list_by_actor_name("三咲まゆ", 1)

        self.assertEqual(raised.exception.status_code, 502)
        self.assertEqual(raised.exception.detail, "upstream")

    async def test_unexpected_error_becomes_500(self):
        with patch.object(
            avbase_router,
            "get_movie_list_by_actor_name_service",
            AsyncMock(side_effect=RuntimeError("boom")),
        ):
            with self.assertRaises(HTTPException) as raised:
                await avbase_router.get_movie_list_by_actor_name("三咲まゆ", 1)

        self.assertEqual(raised.exception.status_code, 500)


if __name__ == "__main__":
    unittest.main()
