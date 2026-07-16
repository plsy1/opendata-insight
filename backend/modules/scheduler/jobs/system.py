from config import _config
from datetime import datetime, timedelta


def clean_cache_dir(max_image_cache_hours=None):
    from pathlib import Path

    CACHE_DIR = _config.get("CACHE_DIR")
    if max_image_cache_hours is None:
        max_image_cache_hours = int(_config.get("IMAGE_CACHE_HOURS"))
    now = datetime.now()
    for f in Path(CACHE_DIR).glob("*"):
        if now - datetime.fromtimestamp(f.stat().st_mtime) > timedelta(
            hours=max_image_cache_hours
        ):
            f.unlink()
