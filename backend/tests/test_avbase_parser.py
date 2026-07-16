import json
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

import modules.metadata.avbase as avbase


def next_data_html(page_props: dict, body: str = "") -> str:
    payload = {"props": {"pageProps": page_props}}
    return (
        "<html><body>"
        f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script>'
        f"{body}</body></html>"
    )


class AvbaseParserTests(unittest.IsolatedAsyncioTestCase):
    async def test_actor_information_uses_current_talent_metadata(self):
        social_body = """
        <div class="group/social col-span-2 mt-4">
          <div class="relative" data-tip="@Mayu_Misaki0801">
            <a href="https://x.com/Mayu_Misaki0801"></a>
          </div>
        </div>
        """
        html = next_data_html(
            {
                "name": "三咲まゆ",
                "talent": {
                    "primary": {
                        "name": "三咲まゆ",
                        "ruby": "みさきまゆ",
                        "image_url": None,
                        "meta": None,
                    },
                    "actors": [{"name": "三咲まゆ"}],
                    "meta": {
                        "basic_info": {"height": "158", "cup": "C"},
                        "sns": [{"sns": "twitter", "id": "Mayu_Misaki0801"}],
                    },
                },
            },
            social_body,
        )

        with patch.object(avbase, "_get_raw_html", AsyncMock(return_value=html)):
            actor = await avbase.parse_actor_information("https://example.test/talent")

        self.assertEqual(actor.name, "三咲まゆ")
        self.assertEqual(actor.ruby, "みさきまゆ")
        self.assertIsNone(actor.avatar_url)
        self.assertEqual(actor.height, "158")
        self.assertEqual(actor.cup, "C")
        self.assertEqual(actor.aliases, ["三咲まゆ"])
        self.assertEqual(len(actor.social_media), 1)
        self.assertEqual(actor.social_media[0].platform, "Twitter")
        self.assertEqual(
            actor.social_media[0].link, "https://x.com/Mayu_Misaki0801"
        )

    async def test_movie_list_uses_next_data_works(self):
        html = next_data_html(
            {
                "works": [
                    {
                        "prefix": "moodyz",
                        "work_id": "MIDA-645",
                        "title": "fallback title",
                        "min_date": "Fri Jul 17 2026 09:00:00 GMT+0900 (Japan Standard Time)",
                        "actors": [{"name": "三咲まゆ"}],
                        "casts": [{"actor": {"name": "共演者"}}],
                        "products": [
                            {
                                "title": "作品タイトル",
                                "date": "Fri Jul 17 2026 09:00:00 GMT+0900 (Japan Standard Time)",
                                "image_url": "https://example.test/mida00645pl.jpg",
                            }
                        ],
                    }
                ]
            }
        )

        with patch.object(avbase, "_get_raw_html", AsyncMock(return_value=html)):
            movies = await avbase.parse_movie_lists("https://example.test/talent")

        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].id, "MIDA-645")
        self.assertEqual(movies[0].full_id, "moodyz:MIDA-645")
        self.assertEqual(movies[0].title, "作品タイトル")
        self.assertEqual(movies[0].release_date, "2026-07-17")
        self.assertEqual(movies[0].img_url, "https://example.test/mida00645pl.jpg")
        self.assertEqual(movies[0].actors, ["三咲まゆ", "共演者"])

    async def test_movie_list_keeps_dom_fallback(self):
        body = """
        <div class="bg-background border border-light rounded-lg overflow-hidden h-full">
          <a href="/works/date/2026-07-17">2026/07/17</a>
          <a href="/works/moodyz:MIDA-645">作品タイトル</a>
          <a href="/talents/mayu">三咲まゆ</a>
          <img loading="lazy" src="https://example.test/mida00645ps.jpg">
        </div>
        """
        html = next_data_html({}, body)

        with patch.object(avbase, "_get_raw_html", AsyncMock(return_value=html)):
            movies = await avbase.parse_movie_lists("https://example.test/talent")

        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].full_id, "moodyz:MIDA-645")
        self.assertEqual(movies[0].release_date, "2026/07/17")
        self.assertEqual(movies[0].actors, ["三咲まゆ"])
        self.assertEqual(movies[0].img_url, "https://example.test/mida00645pl.jpg")

    async def test_missing_next_data_is_reported(self):
        with patch.object(
            avbase,
            "_get_raw_html",
            AsyncMock(return_value="<html><body>missing</body></html>"),
        ):
            with self.assertRaises(HTTPException) as raised:
                await avbase.parse_movie_lists("https://example.test/talent")

        self.assertEqual(raised.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
