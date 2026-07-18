import unittest

from services.torrent_metadata import parse_torrent_title_metadata


class TorrentTitleMetadataTests(unittest.TestCase):
    def test_parses_common_resolution_and_codec_aliases(self):
        cases = [
            ("MIDA-645 [4K] HEVC 10bit", "2160p", "h265"),
            ("MIDA-645.1080p.x264", "1080p", "h264"),
            ("MIDA-645 Full-HD AVC", "1080p", "h264"),
            ("MIDA-645 8K AV1", "4320p", "av1"),
            ("MIDA-645 2K VP9", "1440p", "vp9"),
        ]

        for title, resolution, codec in cases:
            with self.subTest(title=title):
                metadata = parse_torrent_title_metadata(title)
                self.assertEqual(metadata.resolution, resolution)
                self.assertEqual(metadata.codec, codec)

    def test_unknown_metadata_is_left_empty_instead_of_guessed(self):
        metadata = parse_torrent_title_metadata("MIDA-645 original release")

        self.assertIsNone(metadata.resolution)
        self.assertIsNone(metadata.codec)


if __name__ == "__main__":
    unittest.main()
