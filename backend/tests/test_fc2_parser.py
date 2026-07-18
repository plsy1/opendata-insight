import unittest

from modules.metadata.fc2.helper import (
    parse_information,
    parse_ranking,
    parse_seller_information,
    parse_seller_works,
)
from modules.metadata.fc2.model import RankingType


class FC2ParserTests(unittest.TestCase):
    def test_detail_extracts_current_seller_link(self):
        info = parse_information(
            """
            <meta property="og:image" content="https://img.example/cover.jpg">
            <div class="items_article_headerInfo">
              <h3>FC2 work</h3>
              <li>by <a href="https://adult.contents.fc2.com/users/onakin_hemedori/">
                オナキング
              </a></li>
            </div>
            """
        )

        self.assertEqual(info.author, "オナキング")
        self.assertEqual(info.seller_id, "onakin_hemedori")

    def test_ranking_keeps_seller_id_from_owner_link(self):
        items = parse_ranking(
            """
            <div class="c-rankbox-100">
              <div class="c-ranklist-110">
                <h3><a href="/article/?id=12345">Work</a></h3>
                <div class="c-ranklist-110_tmb"><img src="//img.example/a.jpg"></div>
                <div class="c-ranklist-110_own">
                  <a>by</a><a href="/users/onakin_hemedori/">オナキング</a>
                </div>
              </div>
            </div>
            """,
            term=RankingType.daily,
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].owner, "オナキング")
        self.assertEqual(items[0].seller_id, "onakin_hemedori")

    def test_seller_profile_extracts_search_id_and_profile_fields(self):
        seller = parse_seller_information(
            """
            <img src="//img.example/banner.jpg" data-mainVisual>
            <script data-authorId="dccvSJvC"></script>
            <section class="seller_user_account">
              <p data-label="short_intro">X=@seller</p>
              <div class="seller_user_accountIcon">
                <img src="//img.example/avatar.jpg" alt="オナキング"
                     data-image="accountIcon">
              </div>
              <div class="seller_user_accountInfo">
                <h2 data-accountname>オナキング</h2>
                <p><span>商品数 : 66 点</span><span>フォロワー数：4,391人</span></p>
                <div class="seller_user_accountExp"><p>Seller bio</p></div>
              </div>
            </section>
            """,
            "onakin_hemedori",
        )

        self.assertEqual(seller.author_id, "dccvSJvC")
        self.assertEqual(seller.name, "オナキング")
        self.assertEqual(seller.product_count, 66)
        self.assertEqual(seller.follower_count, 4391)
        self.assertEqual(seller.avatar_url, "https://img.example/avatar.jpg")
        self.assertEqual(seller.banner_url, "https://img.example/banner.jpg")

    def test_seller_works_filters_sponsored_cards_from_other_sellers(self):
        def card(article_id: str, seller_id: str, seller_name: str) -> str:
            return f"""
            <div class="c-cntCard-110-f">
              <div class="c-cntCard-110-f_thumb">
                <a href="/article/{article_id}/"><img src="//img.example/{article_id}.jpg"></a>
                <span class="c-cntCard-110-f_thumb_num">01:02:03</span>
              </div>
              <div class="c-cntCard-110-f_indetail">
                <a class="c-cntCard-110-f_itemName" href="/article/{article_id}/"
                   title="Work {article_id}">Work {article_id}</a>
                <p class="c-cntCard-110-f_itemScript">Description</p>
                <span class="c-cntCard-110-f_recom">5</span>
                <span class="c-cntCard-110-f_comment">12</span>
                <span class="c-cntCard-110-f_heart">345</span>
                <span class="c-cntCard-110-f_price">1,000 pt</span>
                <span class="c-cntCard-110-f_seller">by
                  <a href="/users/{seller_id}/">{seller_name}</a>
                </span>
              </div>
            </div>
            """

        result = parse_seller_works(
            f"""
            <div class="search_header"><p>検索結果 66件</p></div>
            <section class="search_cntFlexWp">
              {card("100", "onakin_hemedori", "オナキング")}
              {card("200", "sponsored", "広告卖家")}
            </section>
            <a class="items" href="/search/?author_id=x&page=2">次へ</a>
            """,
            "onakin_hemedori",
        )

        self.assertEqual(result.total, 66)
        self.assertTrue(result.has_next)
        self.assertEqual([work.article_id for work in result.works], ["100"])
        self.assertEqual(result.works[0].favorite_count, 345)


if __name__ == "__main__":
    unittest.main()
