from config import _config
from modules.metadata.avbase import *
from datetime import datetime, timedelta
from services.subscribe import *


def clean_cache_dir(max_image_cache_hours=1):
    from pathlib import Path

    CACHE_DIR = _config.get("CACHE_DIR")
    now = datetime.now()
    for f in Path(CACHE_DIR).glob("*"):
        if now - datetime.fromtimestamp(f.stat().st_mtime) > timedelta(
            hours=max_image_cache_hours
        ):
            f.unlink()
