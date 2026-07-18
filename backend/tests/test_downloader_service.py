import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database import Base
from database.models.fc2 import FC2Product
from database.models.movies import MovieData, MovieProduct
from modules.downloader.qbittorrent import _normalize_keyword_filter
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
        self.db.add(
            FC2Product(
                article_id="1234567",
                product_id="FC2-PPV-1234567",
                title="FC2 database title",
                author="FC2 seller",
                seller_id="fc2-seller",
                cover="https://images.example/fc2-1234567.jpg",
                duration="01:20:30",
                sample_images=[],
            )
        )
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

    def test_fc2_tagged_torrent_returns_cover_and_title_metadata(self):
        result = enrich_downloading_torrents(
            self.db,
            [
                {
                    "hash": "fc2-tagged",
                    "name": "unrelated release name",
                    "tags": "kanojo, fc2-work:1234567",
                }
            ],
        )

        self.assertEqual(result[0]["work_id"], "1234567")
        self.assertEqual(result[0]["media_type"], "fc2")
        self.assertIsNone(result[0]["movie"])
        self.assertEqual(result[0]["fc2_product"].title, "FC2 database title")
        self.assertEqual(result[0]["fc2_product"].author, "FC2 seller")
        self.assertEqual(
            result[0]["fc2_product"].cover,
            "https://images.example/fc2-1234567.jpg",
        )

    def test_legacy_fc2_name_is_matched_without_tag(self):
        result = enrich_downloading_torrents(
            self.db,
            [
                {
                    "hash": "fc2-legacy",
                    "name": "[site] FC2-PPV-1234567 4K",
                    "tags": "kanojo",
                }
            ],
        )

        self.assertEqual(result[0]["work_id"], "1234567")
        self.assertEqual(result[0]["fc2_product"].title, "FC2 database title")

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


class QBKeywordFilterTests(unittest.TestCase):
    def test_accepts_webui_list_format(self):
        self.assertEqual(
            _normalize_keyword_filter(["游戏大全", " 996GG.CC ", ""]),
            ["游戏大全", "996gg.cc"],
        )

    def test_accepts_legacy_comma_separated_format(self):
        self.assertEqual(
            _normalize_keyword_filter("游戏大全, 996GG.CC, 海獺加速"),
            ["游戏大全", "996gg.cc", "海獺加速"],
        )

    def test_accepts_empty_value(self):
        self.assertEqual(_normalize_keyword_filter(None), [])


if __name__ == "__main__":
    unittest.main()
