import os
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch

from app_paths import _copy_legacy_data_if_needed, resolve_data_dir


class AppPathsTests(unittest.TestCase):
    def test_configured_data_directory_is_used(self):
        with tempfile.TemporaryDirectory() as directory:
            configured = Path(directory) / "persistent-data"
            with patch.dict(os.environ, {"KANOJO_DATA_DIR": str(configured)}):
                resolved = resolve_data_dir()

            self.assertEqual(resolved, configured.resolve())
            self.assertTrue(resolved.is_dir())

    def test_legacy_data_is_copied_without_deleting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy" / "data"
            target = root / "backend" / "data"
            legacy.mkdir(parents=True)
            (legacy / "database.db").write_bytes(b"legacy database")
            (legacy / "config.yaml").write_text("key: value\n", encoding="utf-8")

            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")
                _copy_legacy_data_if_needed(target, legacy)

            self.assertEqual(
                (target / "database.db").read_bytes(),
                b"legacy database",
            )
            self.assertEqual(
                (target / "config.yaml").read_text(encoding="utf-8"),
                "key: value\n",
            )
            self.assertTrue((legacy / "database.db").exists())

    def test_existing_target_is_never_overwritten_or_warned_about(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "legacy"
            target = root / "target"
            legacy.mkdir()
            target.mkdir()
            (legacy / "database.db").write_bytes(b"legacy")
            (target / "database.db").write_bytes(b"current")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                _copy_legacy_data_if_needed(target, legacy)

            self.assertEqual((target / "database.db").read_bytes(), b"current")
            self.assertFalse(caught)


if __name__ == "__main__":
    unittest.main()
