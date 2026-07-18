import re
from dataclasses import dataclass


_RESOLUTION_PATTERNS = (
    (
        "4320p",
        re.compile(r"(?<![A-Za-z0-9])(?:4320p?|8k)(?=$|[^A-Za-z])", re.IGNORECASE),
    ),
    (
        "2160p",
        re.compile(
            r"(?<![A-Za-z0-9])(?:2160p?|4k|uhd)(?=$|[^A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    (
        "1440p",
        re.compile(
            r"(?<![A-Za-z0-9])(?:1440p?|2k|qhd)(?=$|[^A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    (
        "1080i",
        re.compile(r"(?<![A-Za-z0-9])1080i(?=$|[^A-Za-z])", re.IGNORECASE),
    ),
    (
        "1080p",
        re.compile(
            r"(?<![A-Za-z0-9])(?:1080p?|fhd|full[\s._-]?hd)(?=$|[^A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    (
        "720p",
        re.compile(r"(?<![A-Za-z0-9])720p?(?=$|[^A-Za-z])", re.IGNORECASE),
    ),
    (
        "576p",
        re.compile(r"(?<![A-Za-z0-9])576[pi]?(?=$|[^A-Za-z])", re.IGNORECASE),
    ),
    (
        "480p",
        re.compile(r"(?<![A-Za-z0-9])480[pi]?(?=$|[^A-Za-z])", re.IGNORECASE),
    ),
)

_CODEC_PATTERNS = (
    (
        "av1",
        re.compile(r"(?<![A-Za-z0-9])av[\s._-]?1(?![A-Za-z])", re.IGNORECASE),
    ),
    (
        "h265",
        re.compile(
            r"(?<![A-Za-z0-9])(?:h[\s._-]?265|x[\s._-]?265|hevc)(?![A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    (
        "h264",
        re.compile(
            r"(?<![A-Za-z0-9])(?:h[\s._-]?264|x[\s._-]?264|avc)(?![A-Za-z])",
            re.IGNORECASE,
        ),
    ),
    (
        "vp9",
        re.compile(r"(?<![A-Za-z0-9])vp[\s._-]?9(?![A-Za-z])", re.IGNORECASE),
    ),
    (
        "mpeg2",
        re.compile(
            r"(?<![A-Za-z0-9])mpeg[\s._-]?2(?![A-Za-z])",
            re.IGNORECASE,
        ),
    ),
)

_RESOLUTION_ALIASES = {
    "8k": "4320p",
    "4320": "4320p",
    "4320p": "4320p",
    "4k": "2160p",
    "uhd": "2160p",
    "2160": "2160p",
    "2160p": "2160p",
    "2k": "1440p",
    "qhd": "1440p",
    "1440": "1440p",
    "1440p": "1440p",
    "fhd": "1080p",
    "fullhd": "1080p",
    "1080": "1080p",
    "1080p": "1080p",
    "1080i": "1080i",
    "720": "720p",
    "720p": "720p",
    "576": "576p",
    "576p": "576p",
    "480": "480p",
    "480p": "480p",
}

_CODEC_ALIASES = {
    "av1": "av1",
    "h265": "h265",
    "x265": "h265",
    "hevc": "h265",
    "h264": "h264",
    "x264": "h264",
    "avc": "h264",
    "vp9": "vp9",
    "mpeg2": "mpeg2",
}


@dataclass(frozen=True)
class TorrentTitleMetadata:
    resolution: str | None = None
    codec: str | None = None


def _normalized_alias_key(value: str) -> str:
    return re.sub(r"[\s._-]", "", value).casefold()


def normalize_resolution(value: str) -> str:
    key = _normalized_alias_key(value)
    return _RESOLUTION_ALIASES.get(key, value.strip().casefold())


def normalize_codec(value: str) -> str:
    key = _normalized_alias_key(value)
    return _CODEC_ALIASES.get(key, value.strip().casefold())


def parse_torrent_title_metadata(title: str) -> TorrentTitleMetadata:
    text = str(title or "")
    resolution = next(
        (
            canonical
            for canonical, pattern in _RESOLUTION_PATTERNS
            if pattern.search(text)
        ),
        None,
    )
    codec = next(
        (canonical for canonical, pattern in _CODEC_PATTERNS if pattern.search(text)),
        None,
    )
    return TorrentTitleMetadata(resolution=resolution, codec=codec)
