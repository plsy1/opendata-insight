import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from database.models.movies import MovieData, MovieProduct, MovieSubscribe
from services.statistic import (
    stat_genres,
    stat_labels,
    stat_makers,
    stat_series,
    stat_tags,
    stat_taxonomy,
)


class StatisticMetadataRankingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        first = MovieData(
            work_id="AAA-001",
            title="First",
            genres=["Drama", "Drama", "Romance"],
            tags=[
                {"name": "Featured"},
                {"name": "Featured"},
                {"name": "Drama"},
            ],
            casts=[],
            actors=[],
        )
        first.products = [
            MovieProduct(
                product_id="one-a",
                url="https://example.com/one-a",
                title="First A",
                maker="Maker A",
                label="Label A",
                series="Series A",
            ),
            MovieProduct(
                product_id="one-b",
                url="https://example.com/one-b",
                title="First B",
                maker="Maker A",
                label="Label A",
                series="Series A",
            ),
        ]
        first.subscribers = MovieSubscribe(is_downloaded=False)

        second = MovieData(
            work_id="BBB-002",
            title="Second",
            genres=["Drama"],
            tags=[{"name": "Featured"}, {"name": "Popular"}],
            casts=[],
            actors=[],
        )
        second.products = [
            MovieProduct(
                product_id="two",
                url="https://example.com/two",
                title="Second",
                maker="Maker A",
                label="Label B",
                series="Series B",
            )
        ]
        second.subscribers = MovieSubscribe(is_downloaded=True)

        self.db.add_all([first, second])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_product_metadata_counts_each_movie_only_once(self):
        self.assertEqual(stat_makers(self.db)[0], {"name": "Maker A", "count": 2})
        self.assertEqual(stat_labels(self.db)[0], {"name": "Label A", "count": 1})
        self.assertEqual(stat_series(self.db)[0], {"name": "Series A", "count": 1})

    def test_json_metadata_deduplicates_values_within_each_movie(self):
        self.assertEqual(stat_genres(self.db)[0], {"name": "Drama", "count": 2})
        self.assertEqual(stat_tags(self.db)[0], {"name": "Featured", "count": 2})

        taxonomy = {
            item["name"]: item["count"] for item in stat_taxonomy(self.db)
        }
        self.assertEqual(taxonomy["Drama"], 2)
        self.assertEqual(taxonomy["Featured"], 2)
        self.assertEqual(taxonomy["Romance"], 1)
        self.assertEqual(taxonomy["Popular"], 1)


if __name__ == "__main__":
    unittest.main()
