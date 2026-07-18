from __future__ import annotations

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect


LEGACY_BASELINE_REVISION = "20260718_0001"
BACKUP_KEEP = 5
LOGGER = logging.getLogger(__name__)
APP_TABLES = {
    "actor_data",
    "actor_subscribe",
    "movie_data",
    "movie_products",
    "movie_subscribe",
    "users",
}


def _alembic_config(database_url: str) -> Config:
    project_dir = Path(__file__).resolve().parents[3]
    config = Config(str(project_dir / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(Path(__file__).resolve().parent),
    )
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def _database_state(engine: Engine) -> tuple[str | None, bool]:
    with engine.connect() as connection:
        current_revision = MigrationContext.configure(connection).get_current_revision()
        tables = set(inspect(connection).get_table_names())
    return current_revision, bool(tables & APP_TABLES)


def _backup_database(database_path: Path, target_revision: str) -> Path:
    backup_dir = database_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_path = backup_dir / (
        f"{database_path.stem}.pre-{target_revision}.{timestamp}{database_path.suffix}"
    )

    with sqlite3.connect(database_path) as source, sqlite3.connect(backup_path) as dest:
        source.backup(dest)

    backups = sorted(
        backup_dir.glob(f"{database_path.stem}.pre-*{database_path.suffix}"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    try:
        keep = max(
            1,
            int(os.environ.get("KANOJO_DATABASE_BACKUP_KEEP", BACKUP_KEEP)),
        )
    except ValueError:
        keep = BACKUP_KEEP
    for old_backup in backups[keep:]:
        old_backup.unlink(missing_ok=True)

    LOGGER.info("Created pre-migration database backup at %s", backup_path)
    return backup_path


def _add_column_if_missing(
    connection,
    table_name: str,
    column_name: str,
    ddl: str,
) -> None:
    inspector = inspect(connection)
    if table_name not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name not in columns:
        connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def _prepare_legacy_database(engine: Engine) -> None:
    from database.base import Base
    import database.models  # noqa: F401

    with engine.begin() as connection:
        Base.metadata.create_all(bind=connection)
        _add_column_if_missing(
            connection,
            "actor_data",
            "updated_at",
            "updated_at DATETIME",
        )
        _add_column_if_missing(
            connection,
            "actor_subscribe",
            "subscribe_order",
            "subscribe_order INTEGER DEFAULT 0 NOT NULL",
        )
        _add_column_if_missing(
            connection,
            "actor_subscribe",
            "collect_order",
            "collect_order INTEGER DEFAULT 0 NOT NULL",
        )


def _run_alembic_command(engine: Engine, config: Config, operation) -> None:
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        operation(config)
    config.attributes.pop("connection", None)


def run_database_migrations(engine: Engine, database_path: Path) -> None:
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    config = _alembic_config(str(engine.url))
    scripts = ScriptDirectory.from_config(config)
    head_revision = scripts.get_current_head()
    current_revision, has_app_tables = _database_state(engine)

    if current_revision == head_revision:
        LOGGER.info("Database schema is current at revision %s", head_revision)
        return

    if has_app_tables and database_path.exists():
        _backup_database(database_path, head_revision)

    if current_revision is None and has_app_tables:
        _prepare_legacy_database(engine)
        _run_alembic_command(
            engine,
            config,
            lambda cfg: command.stamp(cfg, LEGACY_BASELINE_REVISION),
        )

    _run_alembic_command(
        engine,
        config,
        lambda cfg: command.upgrade(cfg, "head"),
    )
    LOGGER.info(
        "Database schema upgraded from %s to %s",
        current_revision or "legacy/unversioned",
        head_revision,
    )
