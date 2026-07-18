import unittest
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from database.models.actors import ActorData
from database.models.movies import MovieData, MovieProduct, MovieSubscribe
from schemas.actor import ActorDataOut
from schemas.feed import MovieSubscriptionRulesUpdate
from services.subscribe import (
    MovieStatus,
    Operation,
    actor_operation_service,
    movie_subscribe_list_service,
    update_movie_subscription_rules_service,
)


class MovieFeedTests(unittest.TestCase):
    def test_feed_keeps_card_fields_and_complete_movie(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        with Session(engine) as db:
            movie = MovieData(
                work_id="FEED-001",
                prefix="dvd",
                title="Feed movie",
                casts=[{"name": "Actor A"}],
                actors=[],
                tags=[{"name": "Tag A"}],
                genres=["Genre A"],
            )
            movie.products = [
                MovieProduct(
                    product_id="store-a",
                    url="https://store.example/item",
                    title="Product title",
                    image_url="cover.jpg",
                    sample_image_urls=[{"l": "sample.jpg"}],
                )
            ]
            movie.subscribers = MovieSubscribe(is_downloaded=False)
            db.add(movie)
            db.commit()

            result = movie_subscribe_list_service(db, MovieStatus.SUBSCRIBE)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].id, "FEED-001")
            self.assertEqual(result[0].movie.work_id, "FEED-001")
            self.assertEqual(result[0].movie.products[0].product_id, "store-a")
            self.assertFalse(result[0].movie.subscribers.is_downloaded)
            self.assertTrue(result[0].subscription_rules.use_global)

            updated = update_movie_subscription_rules_service(
                db,
                "FEED-001",
                MovieSubscriptionRulesUpdate(
                    use_global=False,
                    global_excluded_keywords=["预告片"],
                    quality_rules=[
                        {
                            "resolution": "2160p",
                            "codec": "h265",
                            "required_keywords": ["中文字幕"],
                        }
                    ],
                ),
            )
            self.assertTrue(updated)

            custom_result = movie_subscribe_list_service(
                db,
                MovieStatus.SUBSCRIBE,
            )
            self.assertFalse(custom_result[0].subscription_rules.use_global)
            self.assertEqual(
                custom_result[0].subscription_rules.global_excluded_keywords,
                ["预告片"],
            )
            self.assertEqual(
                custom_result[0].subscription_rules.quality_rules[0].resolution,
                "2160p",
            )

        engine.dispose()


class ActorSubscriptionTests(unittest.IsolatedAsyncioTestCase):
    async def test_first_subscription_does_not_duplicate_actor(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        async def fetch_actor(_name: str) -> ActorDataOut:
            return ActorDataOut(name="Actor A", aliases=[], social_media=[])

        with Session(engine) as db, patch(
            "services.avbase.fetch_actor_information_from_source",
            new=AsyncMock(side_effect=fetch_actor),
        ):
            result = await actor_operation_service(
                db,
                "Actor A",
                Operation.SUBSCRIBE,
            )

            actors = db.query(ActorData).filter(ActorData.name == "Actor A").all()
            self.assertTrue(result)
            self.assertEqual(len(actors), 1)
            self.assertTrue(actors[0].subscribers.is_subscribe)

        engine.dispose()


if __name__ == "__main__":
    unittest.main()
