import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import ActorData, AvbaseReleaseCache, Base
from database.models.movies import MovieData, MovieProduct, MovieSubscribe
from schemas.actor import ActorDataOut
from services.avbase import (
    AVBASE_DETAIL_SOURCE,
    AVBASE_RELEASE_SOURCE,
    _actor_cache_expired,
    cleanup_avbase_release_cache,
    fetch_avbase_release_by_date_and_write_db,
    get_actor_information_by_name_service,
    get_information_by_work_id_service,
    get_release_service,
    refresh_information_by_work_id_service,
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


class ActorInformationTests(unittest.IsolatedAsyncioTestCase):
    async def test_refresh_never_overwrites_actor_primary_key(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            actor = ActorData(
                name="Actor A",
                avatar_url=None,
                updated_at=datetime(2026, 1, 1),
            )
            db.add(actor)
            db.commit()
            actor_id = actor.id

            source_data = ActorDataOut(
                id=None,
                name="Unexpected replacement name",
                avatar_url="https://example.com/actor.jpg",
                updated_at=None,
            )
            with patch(
                "services.avbase.fetch_actor_information_from_source",
                new=AsyncMock(return_value=source_data),
            ):
                result = await get_actor_information_by_name_service(
                    db,
                    "Actor A",
                )

            refreshed = db.get(ActorData, actor_id)
            self.assertIsNotNone(refreshed)
            self.assertEqual(result.id, actor_id)
            self.assertEqual(refreshed.id, actor_id)
            self.assertEqual(refreshed.name, "Actor A")
            self.assertEqual(
                refreshed.avatar_url,
                "https://example.com/actor.jpg",
            )

        engine.dispose()


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
            movie = db.query(MovieData).one()
            self.assertEqual(movie.source_type, AVBASE_DETAIL_SOURCE)
            self.assertIsNotNone(movie.last_seen_at)
            self.assertIsNotNone(movie.metadata_updated_at)

        engine.dispose()

    async def test_stale_refresh_reconciles_movie_and_product_metadata(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        refreshed_work = {
            "work_id": "REFRESH-001",
            "prefix": "dvd",
            "title": "Updated movie",
            "min_date": "2026-07-20",
            "casts": [{"actor": {"name": "Updated actor"}}],
            "actors": [],
            "tags": [],
            "genres": [{"name": "Updated genre"}],
            "products": [
                {
                    "product_id": "store-a",
                    "url": "https://store.example/a",
                    "title": "Updated product",
                    "image_url": "updated-cover.jpg",
                },
                {
                    "product_id": "store-b",
                    "url": "https://store.example/b",
                    "title": "New product",
                },
            ],
        }

        with Session(engine) as db:
            movie = MovieData(
                work_id="REFRESH-001",
                title="Old movie",
                metadata_updated_at=datetime(2026, 1, 1),
            )
            movie.products = [
                MovieProduct(
                    product_id="store-a",
                    url="https://store.example/old-a",
                    title="Old product",
                ),
                MovieProduct(
                    product_id="removed-store",
                    url="https://store.example/removed",
                    title="Removed product",
                ),
            ]
            db.add(movie)
            db.commit()

            with patch(
                "services.avbase.avbase_client.fetch_html",
                new=AsyncMock(return_value="<html></html>"),
            ), patch(
                "services.avbase.parse_movie_information",
                return_value=refreshed_work,
            ):
                result = await refresh_information_by_work_id_service(
                    db,
                    "dvd:REFRESH-001",
                    max_age=timedelta(days=3),
                )

            self.assertEqual(result.title, "Updated movie")
            self.assertEqual(result.genres, ["Updated genre"])
            self.assertEqual(
                [product.product_id for product in result.products],
                ["store-a", "store-b"],
            )
            self.assertEqual(result.products[0].title, "Updated product")
            self.assertIsNotNone(result.metadata_updated_at)

        engine.dispose()

    async def test_fresh_metadata_skips_remote_refresh(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            movie = MovieData(
                work_id="FRESH-001",
                title="Fresh movie",
                metadata_updated_at=datetime.now(),
            )
            movie.products = [
                MovieProduct(
                    product_id="store-a",
                    url="https://store.example/a",
                    title="Fresh product",
                )
            ]
            db.add(movie)
            db.commit()

            fetch = AsyncMock(return_value="<html></html>")
            with patch("services.avbase.avbase_client.fetch_html", new=fetch):
                result = await refresh_information_by_work_id_service(
                    db,
                    "FRESH-001",
                    max_age=timedelta(days=3),
                )

            self.assertEqual(result.title, "Fresh movie")
            fetch.assert_not_awaited()

        engine.dispose()

    async def test_failed_refresh_preserves_existing_metadata(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            movie = MovieData(
                work_id="STALE-001",
                title="Preserved movie",
                metadata_updated_at=datetime(2026, 1, 1),
            )
            movie.products = [
                MovieProduct(
                    product_id="store-a",
                    url="https://store.example/a",
                    title="Preserved product",
                )
            ]
            db.add(movie)
            db.commit()

            with patch(
                "services.avbase.avbase_client.fetch_html",
                new=AsyncMock(side_effect=HTTPException(status_code=502)),
            ):
                with self.assertRaises(HTTPException):
                    await refresh_information_by_work_id_service(
                        db,
                        "STALE-001",
                        max_age=timedelta(days=3),
                    )

            preserved = db.query(MovieData).filter_by(work_id="STALE-001").one()
            self.assertEqual(preserved.title, "Preserved movie")
            self.assertEqual(preserved.products[0].title, "Preserved product")
            self.assertEqual(
                preserved.metadata_updated_at,
                datetime(2026, 1, 1),
            )

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
                source_type=AVBASE_RELEASE_SOURCE,
                last_seen_at=datetime(2026, 1, 1),
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

            self.assertEqual(
                [item.product_id for item in result.products],
                ["store-a", "store-b"],
            )
            self.assertEqual(result.primary_product.image_url, "cover-b.jpg")
            self.assertEqual(
                result.primary_product.sample_image_urls,
                [{"l": "sample-a.jpg"}, {"l": "sample-b.jpg"}],
            )
            self.assertEqual(movie.source_type, AVBASE_DETAIL_SOURCE)
            self.assertGreater(movie.last_seen_at, datetime(2026, 1, 1))

        engine.dispose()

    async def test_release_fetch_marks_new_cache_without_downgrading_detail(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        works = [
            {
                "work_id": "RELEASE-001",
                "prefix": "dvd",
                "title": "Release movie",
                "min_date": "2026-07-18",
                "casts": [],
                "actors": [],
                "tags": [],
                "genres": [],
                "products": [],
            },
            {
                "work_id": "DETAIL-001",
                "prefix": "dvd",
                "title": "Detail movie",
                "min_date": "2026-07-18",
                "casts": [],
                "actors": [],
                "tags": [],
                "genres": [],
                "products": [],
            },
        ]

        with Session(engine) as db:
            db.add(
                MovieData(
                    work_id="DETAIL-001",
                    source_type=AVBASE_DETAIL_SOURCE,
                    last_seen_at=datetime(2026, 1, 1),
                )
            )
            db.commit()

            with patch(
                "services.avbase._get_every_day_release",
                new=AsyncMock(return_value=works),
            ):
                await fetch_avbase_release_by_date_and_write_db(
                    db,
                    "2026-07-18",
                )

            records = {
                record.work_id: record for record in db.query(MovieData).all()
            }
            self.assertEqual(
                records["RELEASE-001"].source_type,
                AVBASE_RELEASE_SOURCE,
            )
            self.assertEqual(
                records["DETAIL-001"].source_type,
                AVBASE_DETAIL_SOURCE,
            )
            self.assertGreater(
                records["DETAIL-001"].last_seen_at,
                datetime(2026, 1, 1),
            )
            cache = db.get(AvbaseReleaseCache, "2026-07-18")
            self.assertIsNotNone(cache)
            self.assertIsNotNone(cache.fetched_at)

        engine.dispose()


class ReleaseCacheCleanupTests(unittest.TestCase):
    def test_only_expired_unsubscribed_release_records_are_deleted(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        now = datetime(2026, 7, 18, 12, 0, 0)

        def movie(work_id, source_type, last_seen_at):
            record = MovieData(
                work_id=work_id,
                source_type=source_type,
                last_seen_at=last_seen_at,
            )
            record.products = [
                MovieProduct(
                    product_id=f"product-{work_id}",
                    url=f"https://example.com/{work_id}",
                )
            ]
            return record

        with Session(engine) as db:
            expired = movie(
                "OLD-001",
                AVBASE_RELEASE_SOURCE,
                now - timedelta(days=31),
            )
            subscribed = movie(
                "OLD-002",
                AVBASE_RELEASE_SOURCE,
                now - timedelta(days=31),
            )
            subscribed.subscribers = MovieSubscribe(is_downloaded=False)
            recent = movie(
                "NEW-001",
                AVBASE_RELEASE_SOURCE,
                now - timedelta(days=30),
            )
            detail = movie(
                "DETAIL-001",
                AVBASE_DETAIL_SOURCE,
                now - timedelta(days=365),
            )
            old_cache = AvbaseReleaseCache(
                release_date="2026-01-01",
                fetched_at=now - timedelta(days=31),
            )
            recent_cache = AvbaseReleaseCache(
                release_date="2026-07-18",
                fetched_at=now - timedelta(days=30),
            )
            db.add_all([expired, subscribed, recent, detail])
            db.add_all([old_cache, recent_cache])
            db.commit()

            deleted = cleanup_avbase_release_cache(
                db,
                retention_days=30,
                batch_size=1,
                now=now,
            )

            self.assertEqual(deleted, 1)
            self.assertEqual(
                {record.work_id for record in db.query(MovieData).all()},
                {"OLD-002", "NEW-001", "DETAIL-001"},
            )
            self.assertEqual(db.query(MovieProduct).count(), 3)
            self.assertIsNone(db.get(AvbaseReleaseCache, "2026-01-01"))
            self.assertIsNotNone(db.get(AvbaseReleaseCache, "2026-07-18"))

        engine.dispose()


class ReleaseCacheReadTests(unittest.IsolatedAsyncioTestCase):
    async def test_incomplete_historical_date_is_refetched_without_marker(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            detail = MovieData(
                work_id="DETAIL-001",
                min_date="2020-01-01",
                title="Preserved detail",
                source_type=AVBASE_DETAIL_SOURCE,
                last_seen_at=datetime(2026, 7, 18),
            )
            detail.products = [
                MovieProduct(
                    product_id="detail-product",
                    url="https://example.com/detail",
                    title="Preserved detail",
                    maker="Example",
                )
            ]
            db.add(detail)
            db.commit()

            with patch(
                "services.avbase.fetch_avbase_release_by_date_and_write_db",
                new=AsyncMock(),
            ) as fetch:
                result = await get_release_service(db, "2020-01-01")

            fetch.assert_awaited_once_with(db, "2020-01-01")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["works"][0]["id"], "DETAIL-001")

        engine.dispose()


if __name__ == "__main__":
    unittest.main()
