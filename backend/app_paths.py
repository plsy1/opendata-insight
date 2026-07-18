import os
import shutil
import sys
import warnings
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BACKEND_DIR / "data"
DATA_DIR_ENV = "KANOJO_DATA_DIR"


def _contains_persistent_data(path: Path) -> bool:
    return any((path / name).exists() for name in ("database.db", "config.yaml"))


def _legacy_runtime_data_dir(argv0: str | None = None) -> Path:
    executable = Path(argv0 or sys.argv[0]).expanduser()
    try:
        executable = executable.resolve()
    except OSError:
        executable = executable.absolute()
    return executable.parent / "data"


def _copy_legacy_data_if_needed(target: Path, legacy: Path) -> None:
    if legacy == target or not _contains_persistent_data(legacy):
        return

    if _contains_persistent_data(target):
        # The stable backend data directory is authoritative once initialized.
        # Keep the legacy copy untouched so it can still be recovered manually,
        # but do not emit a warning on every application startup.
        return

    target.mkdir(parents=True, exist_ok=True)
    for name in ("database.db", "config.yaml"):
        source = legacy / name
        if source.exists():
            shutil.copy2(source, target / name)

    legacy_cache = legacy / "cache_images"
    if legacy_cache.is_dir():
        shutil.copytree(
            legacy_cache,
            target / "cache_images",
            dirs_exist_ok=True,
        )

    warnings.warn(
        f"Copied persistent data from the legacy runtime directory {legacy} "
        f"to the stable directory {target}. The legacy copy was preserved.",
        RuntimeWarning,
        stacklevel=2,
    )


def resolve_data_dir() -> Path:
    configured = os.environ.get(DATA_DIR_ENV)
    if configured:
        data_dir = Path(configured).expanduser().resolve()
    else:
        data_dir = DEFAULT_DATA_DIR
        _copy_legacy_data_if_needed(data_dir, _legacy_runtime_data_dir())

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR = resolve_data_dir()
DATABASE_PATH = DATA_DIR / "database.db"
CONFIG_PATH = DATA_DIR / "config.yaml"
IMAGE_CACHE_DIR = DATA_DIR / "cache_images"
