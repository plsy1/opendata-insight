import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from database.base import Base
from database.models.images import ImageSource
from routers.system import _serve_image
import services.system as image_service
from services.system import (
    CachedImage,
    fetch_and_cache_image,
    image_id_for_url,
    register_image_sources,
    replace_domain_in_value,
)


class ImageMappingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_image_id_mapping_is_stable_and_persistent(self):
        source_url = "https://example.test/posters/movie.jpg"
        expected_id = image_id_for_url(source_url)

        first = register_image_sources([source_url], db=self.db)
        second = register_image_sources([source_url], db=self.db)

        self.assertEqual(first, {expected_id: source_url})
        self.assertEqual(second, first)
        record = self.db.get(ImageSource, expected_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.source_url, source_url)

    def test_external_images_become_stable_backend_urls(self):
        source_url = "https://www.avbase.net/images/actor.jpg"
        with patch("services.system.register_image_sources") as register:
            result = replace_domain_in_value(
                {
                    "avatar_url": source_url,
                    "profile_url": "https://www.avbase.net/talents/example",
                }
            )

        expected_id = image_id_for_url(source_url)
        self.assertEqual(
            result["avatar_url"],
            f"/api/v1/system/images/{expected_id}",
        )
        self.assertEqual(
            result["profile_url"],
            "https://www.avbase.net/talents/example",
        )
        self.assertEqual(list(register.call_args.args[0]), [source_url])


class ImageResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_cache_misses_fetch_upstream_once(self):
        calls = 0

        async def upstream(_request):
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.01)
            return httpx.Response(
                200,
                content=b"image-bytes",
                headers={"content-type": "image/webp", "etag": '"source-etag"'},
            )

        source = SimpleNamespace(
            image_id="b" * 64,
            source_url="https://example.test/image",
            content_type=None,
            content_etag=None,
            upstream_etag=None,
            upstream_last_modified=None,
        )
        previous_client = image_service._image_http_client
        previous_cache_dir = image_service.CACHE_DIR
        with tempfile.TemporaryDirectory() as directory:
            image_service.CACHE_DIR = Path(directory)
            image_service._image_runtime_metadata.clear()
            image_service._image_http_client = httpx.AsyncClient(
                transport=httpx.MockTransport(upstream)
            )
            try:
                first, second = await asyncio.gather(
                    fetch_and_cache_image(source),
                    fetch_and_cache_image(source),
                )
            finally:
                await image_service._image_http_client.aclose()
                image_service._image_http_client = previous_client
                image_service.CACHE_DIR = previous_cache_dir
                image_service._image_runtime_metadata.clear()

        self.assertEqual(calls, 1)
        self.assertEqual(first.content_type, "image/webp")
        self.assertEqual(second.content_type, "image/webp")
        self.assertEqual(first.content_etag, second.content_etag)

    async def test_matching_etag_returns_304(self):
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/system/images/id",
                "headers": [(b"if-none-match", b'"content-etag"')],
            }
        )
        source = SimpleNamespace(image_id="a" * 64)
        with tempfile.TemporaryDirectory() as directory:
            cached = CachedImage(
                path=Path(directory) / "cached-image",
                content_type="image/webp",
                content_etag="content-etag",
            )
            with patch(
                "routers.system.get_image_source",
                return_value=source,
            ), patch(
                "routers.system.fetch_and_cache_image",
                AsyncMock(return_value=cached),
            ), patch("routers.system.update_image_source_metadata"):
                response = await _serve_image(request, object(), "a" * 64)

        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.headers["cache-control"].split(",")[0], "private")
        self.assertEqual(response.headers["vary"], "Cookie")

    async def test_unknown_image_id_returns_404(self):
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/system/images/missing",
                "headers": [],
            }
        )
        with patch("routers.system.get_image_source", return_value=None):
            with self.assertRaises(HTTPException) as raised:
                await _serve_image(request, object(), "missing")

        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
