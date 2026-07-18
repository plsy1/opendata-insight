import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from database.models.movies import MovieData, MovieProduct
from services.avbase import (
    _actor_cache_expired,
    get_information_by_work_id_service,
)


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


class MovieInformationTests(unittest.IsolatedAsyncioTestCase):
    async def test_uncached_detail_persists_response_dto_safely(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        work = {
            "work_id": "NEW-001",
            "prefix": "dvd",
            "title": "New movie",
            "min_date": "2026-07-18",
            "casts": [],
            "actors": [],
            "tags": [],
            "genres": [],
            "products": [
                {
                    "product_id": "store-new",
                    "url": "https://store.example/new",
                    "title": "New product",
                    "image_url": "new-cover.jpg",
                }
            ],
        }

        with Session(engine) as db, patch(
            "services.avbase.avbase_client.fetch_html",
            new=AsyncMock(return_value="<html></html>"),
        ), patch("services.avbase.parse_movie_information", return_value=work):
            result = await get_information_by_work_id_service(db, "dvd:NEW-001")

            self.assertEqual(result.work_id, "NEW-001")
            self.assertEqual(result.primary_product.product_id, "store-new")
            self.assertEqual(db.query(MovieData).count(), 1)
            self.assertEqual(db.query(MovieProduct).count(), 1)

        engine.dispose()

    async def test_detail_keeps_all_products_and_exposes_merged_primary(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            movie = MovieData(
                work_id="TEST-001",
                prefix="dvd",
                title="Complete movie",
                casts=[],
                actors=[],
                tags=[],
                genres=[],
            )
            movie.products = [
                MovieProduct(
                    product_id="store-a",
                    url="https://store-a.example/item",
                    title="Store A title",
                    image_url=None,
                    sample_image_urls=[{"l": "sample-a.jpg"}],
                ),
                MovieProduct(
                    product_id="store-b",
                    url="https://store-b.example/item",
                    title="Store B title",
                    image_url="cover-b.jpg",
                    sample_image_urls=[{"l": "sample-b.jpg"}],
                ),
            ]
            db.add(movie)
            db.commit()

            result = await get_information_by_work_id_service(db, "TEST-001")

            self.assertEqual([item.product_id for item in result.products], ["store-a", "store-b"])
            self.assertEqual(result.primary_product.image_url, "cover-b.jpg")
            self.assertEqual(
                result.primary_product.sample_image_urls,
                [{"l": "sample-a.jpg"}, {"l": "sample-b.jpg"}],
            )

        engine.dispose()


if __name__ == "__main__":
    unittest.main()
