import tempfile
import unittest
from pathlib import Path

import yaml

from config import ConfigManager


class SubscriptionConfigMigrationTests(unittest.TestCase):
    def test_media_paths_fall_back_to_legacy_download_path(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(
                    {
                        "DOWNLOAD_PATH": "/media/default",
                        "FC2_DOWNLOAD_PATH": "/media/fc2",
                    }
                ),
                encoding="utf-8",
            )

            manager = object.__new__(ConfigManager)
            manager._init(str(config_path))

            self.assertEqual(manager.get_download_path("jav"), "/media/default")
            self.assertEqual(manager.get_download_path("fc2"), "/media/fc2")

    def test_legacy_global_filters_are_moved_into_priority_groups(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text(
                yaml.safe_dump(
                    {
                        "SUBSCRIBE_TITLE_REQUIRED": ["中文字幕"],
                        "SUBSCRIBE_TITLE_ANY": ["无码", "破解"],
                        "SUBSCRIBE_TITLE_EXCLUDED": ["广告", "预告片"],
                        "SUBSCRIBE_TITLE_REGEX": r"MIDA[-_ ]?\d+",
                        "SUBSCRIBE_QUALITY_RULES": [
                            {"resolution": "2160p", "codec": "h265"},
                            {"resolution": "1080p", "codec": "h264"},
                        ],
                    },
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )

            manager = object.__new__(ConfigManager)
            manager._init(str(config_path))
            environment = manager.get_environment()

            self.assertEqual(
                environment["SUBSCRIBE_GLOBAL_EXCLUDED"],
                ["广告", "预告片"],
            )
            for rule in environment["SUBSCRIBE_QUALITY_RULES"]:
                self.assertEqual(rule["required_keywords"], ["中文字幕"])
                self.assertEqual(rule["any_keywords"], ["无码", "破解"])
                self.assertEqual(rule["excluded_keywords"], [])
                self.assertEqual(rule["title_regex"], r"MIDA[-_ ]?\d+")


if __name__ == "__main__":
    unittest.main()
