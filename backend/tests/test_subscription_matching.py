import unittest

from pydantic import ValidationError

from schemas.system import EnvironmentConfig
from services.subscribe import (
    subscription_rules_from_values,
    select_best_subscription_resource,
)


class SubscriptionMatchingTests(unittest.TestCase):
    def test_empty_rule_keeps_highest_seeder_behavior(self):
        results = [
            {"title": "MIDA-645 1080p", "seeders": 12},
            {"title": "MIDA-645 4K", "seeders": 35},
        ]

        selected = select_best_subscription_resource(results)

        self.assertEqual(selected["title"], "MIDA-645 4K")

    def test_combined_rules_filter_before_sorting(self):
        rules = subscription_rules_from_values(
            [
                {
                    "resolution": "4K",
                    "codec": "HEVC",
                    "required_keywords": "MIDA-645，字幕",
                    "any_keywords": ["无码", "破解"],
                    "excluded_keywords": "合集; trailer",
                    "title_regex": r"MIDA[-_ ]?645",
                }
            ]
        )
        results = [
            {"title": "MIDA-645 4K HEVC 中文字幕 无码 合集", "seeders": 100},
            {"title": "mida-645 2160p x265 中文字幕 破解", "seeders": 20},
            {"title": "MIDA-645 1080p AVC 中文字幕 无码", "seeders": 80},
        ]

        selected = select_best_subscription_resource(results, rules)

        self.assertEqual(selected["title"], "mida-645 2160p x265 中文字幕 破解")

    def test_no_match_does_not_fall_back_to_unmatched_resource(self):
        rules = subscription_rules_from_values(
            [{"required_keywords": ["4K"]}]
        )

        selected = select_best_subscription_resource(
            [{"title": "MIDA-645 1080p", "seeders": 100}],
            rules,
        )

        self.assertIsNone(selected)

    def test_quality_rule_groups_are_matched_in_priority_order(self):
        rules = subscription_rules_from_values(
            [
                {"resolution": "4K", "codec": "HEVC"},
                {"resolution": "1080p", "codec": "H.264"},
            ]
        )
        results = [
            {"title": "MIDA-645 1080p x264", "seeders": 100},
            {"title": "MIDA-645 UHD HEVC 10bit", "seeders": 12},
        ]

        selected = select_best_subscription_resource(
            results,
            rules=rules,
        )

        self.assertEqual(selected["title"], "MIDA-645 UHD HEVC 10bit")

    def test_quality_matching_falls_through_to_next_group(self):
        rules = subscription_rules_from_values(
            [
                {"resolution": "4K", "codec": "AV1"},
                {"resolution": "1080p", "codec": "H.264"},
            ]
        )

        selected = select_best_subscription_resource(
            [{"title": "MIDA-645 1080p AVC", "seeders": 20}],
            rules=rules,
        )

        self.assertEqual(selected["title"], "MIDA-645 1080p AVC")

    def test_quality_rules_do_not_fall_back_when_no_group_matches(self):
        rules = subscription_rules_from_values(
            [{"resolution": "4K", "codec": "AV1"}]
        )

        selected = select_best_subscription_resource(
            [{"title": "MIDA-645 1080p AVC", "seeders": 100}],
            rules=rules,
        )

        self.assertIsNone(selected)

    def test_global_excluded_keywords_apply_before_all_groups(self):
        rules = subscription_rules_from_values(
            [{"resolution": None, "codec": None}]
        )
        results = [
            {"title": "MIDA-645 4K 广告", "seeders": 100},
            {"title": "MIDA-645 1080p", "seeders": 10},
        ]

        selected = select_best_subscription_resource(
            results,
            rules,
            global_excluded_keywords="广告，预告片",
        )

        self.assertEqual(selected["title"], "MIDA-645 1080p")

    def test_environment_normalizes_keywords_and_rejects_invalid_regex(self):
        config = EnvironmentConfig(
            SUBSCRIBE_GLOBAL_EXCLUDED="广告，预告片\n合集",
        )
        self.assertEqual(
            config.SUBSCRIBE_GLOBAL_EXCLUDED,
            ["广告", "预告片", "合集"],
        )
        quality_config = EnvironmentConfig(
            SUBSCRIBE_QUALITY_RULES=[
                {
                    "resolution": "2160p",
                    "codec": "h265",
                    "required_keywords": "中文字幕，破解",
                },
                {"resolution": None, "codec": None},
            ]
        )
        self.assertEqual(len(quality_config.SUBSCRIBE_QUALITY_RULES), 2)
        self.assertEqual(
            quality_config.SUBSCRIBE_QUALITY_RULES[0].required_keywords,
            ["中文字幕", "破解"],
        )

        with self.assertRaises(ValidationError):
            EnvironmentConfig(
                SUBSCRIBE_QUALITY_RULES=[{"title_regex": "["}]
            )


if __name__ == "__main__":
    unittest.main()
