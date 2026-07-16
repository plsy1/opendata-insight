import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from modules.metadata.avbase.client import AvbaseClient


VALID_HTML = '<script id="__NEXT_DATA__">{}</script>'


class AvbaseClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_http_is_preferred_when_response_contains_next_data(self):
        client = AvbaseClient(http_retries=0)
        with patch.object(
            client, "_fetch_http", AsyncMock(return_value=VALID_HTML)
        ), patch.object(client, "_fetch_browser", AsyncMock()) as browser_fetch:
            result = await client.fetch_html("https://example.test")

        self.assertEqual(result, VALID_HTML)
        browser_fetch.assert_not_awaited()

    async def test_browser_is_fallback_for_invalid_http_response(self):
        client = AvbaseClient(http_retries=0)
        with patch.object(
            client, "_fetch_http", AsyncMock(return_value="missing data")
        ), patch.object(
            client, "_fetch_browser", AsyncMock(return_value=VALID_HTML)
        ) as browser_fetch:
            result = await client.fetch_html("https://example.test")

        self.assertEqual(result, VALID_HTML)
        browser_fetch.assert_awaited_once()

    async def test_http_404_is_preserved_without_browser_fallback(self):
        client = AvbaseClient(http_retries=0)
        not_found = HTTPException(status_code=404, detail="missing")
        with patch.object(
            client, "_fetch_http", AsyncMock(side_effect=not_found)
        ), patch.object(client, "_fetch_browser", AsyncMock()) as browser_fetch:
            with self.assertRaises(HTTPException) as raised:
                await client.fetch_html("https://example.test")

        self.assertEqual(raised.exception.status_code, 404)
        browser_fetch.assert_not_awaited()

    async def test_concurrency_is_limited(self):
        client = AvbaseClient(max_concurrency=2, http_retries=0)
        active = 0
        peak = 0

        async def fake_http(_url):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.01)
            active -= 1
            return VALID_HTML

        with patch.object(client, "_fetch_http", side_effect=fake_http), patch.object(
            client, "_fetch_browser", AsyncMock()
        ):
            await asyncio.gather(
                *(client.fetch_html(f"https://example.test/{index}") for index in range(5))
            )

        self.assertEqual(peak, 2)


if __name__ == "__main__":
    unittest.main()
