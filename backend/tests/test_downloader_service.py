import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from database.models.movies import MovieData, MovieProduct
from services.downloader import (
    build_download_tags,
    enrich_downloading_torrents,
    resolve_download_media_type,
)


class DownloadMetadataTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)

        movie = MovieData(
            work_id="MIDA-645",
            prefix="moodyz",
            title="Database movie title",
            casts=[{"name": "Actor A"}],
            actors=[],
            tags=[{"name": "Tag A"}],
            genres=["Genre A"],
        )
        movie.products = [
            MovieProduct(
                product_id="store-a",
                url="https://store.example/mida-645",
                title="Product title",
                image_url="https://images.example/mida-645.jpg",
                sample_image_urls=[],
            )
        ]
        self.db.add(movie)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_work_id_tag_is_added_without_losing_base_tag(self):
        self.assertEqual(
            build_download_tags("kanojo", "moodyz:MIDA-645"),
            "kanojo,avbase-work:MIDA-645",
        )

    def test_fc2_download_uses_its_own_tag_and_media_type(self):
        self.assertEqual(resolve_download_media_type("", "1234567"), "fc2")
        self.assertEqual(
            build_download_tags("kanojo", "1234567", "fc2"),
            "kanojo,fc2-work:1234567",
        )

    def test_tagged_torrent_returns_complete_movie(self):
        result = enrich_downloading_torrents(
            self.db,
            [
                {
                    "hash": "tagged",
                    "name": "unrelated release name",
                    "tags": "kanojo, avbase-work:MIDA-645",
                }
            ],
        )

        self.assertEqual(result[0]["work_id"], "MIDA-645")
        self.assertEqual(result[0]["movie"].title, "Database movie title")
        self.assertEqual(result[0]["movie"].products[0].product_id, "store-a")
        self.assertEqual(
            result[0]["movie"].primary_product.image_url,
            "https://images.example/mida-645.jpg",
        )

    def test_legacy_torrent_name_is_matched_without_tag(self):
        result = enrich_downloading_torrents(
            self.db,
            [{"hash": "legacy", "name": "[site] mida00645 1080p", "tags": "kanojo"}],
        )

        self.assertEqual(result[0]["work_id"], "MIDA-645")
        self.assertEqual(result[0]["movie"].title, "Database movie title")

    def test_unknown_torrent_keeps_null_movie(self):
        result = enrich_downloading_torrents(
            self.db,
            [{"hash": "unknown", "name": "unmatched", "tags": "kanojo"}],
        )

        self.assertIsNone(result[0]["work_id"])
        self.assertIsNone(result[0]["movie"])


if __name__ == "__main__":
    unittest.main()
