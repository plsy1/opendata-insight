import sqlite3
import tempfile
import unittest
from pathlib import Path

from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

from database.base import configure_sqlite_connection
from database.migrations.runner import run_database_migrations


class DatabaseMigrationTests(unittest.TestCase):
    def _engine(self, database_path: Path):
        return create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False, "timeout": 5},
        )

    def test_fresh_database_is_created_at_head(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "database.db"
            engine = self._engine(database_path)

            run_database_migrations(engine, database_path)

            inspector = inspect(engine)
            self.assertIn("movie_data", inspector.get_table_names())
            self.assertIn("image_sources", inspector.get_table_names())
            self.assertIn("alembic_version", inspector.get_table_names())
            movie_indexes = {
                index["name"] for index in inspector.get_indexes("movie_data")
            }
            self.assertIn("ix_movie_data_min_date", movie_indexes)
            subscribe_columns = {
                column["name"]
                for column in inspector.get_columns("movie_subscribe")
            }
            self.assertIn("rule_config", subscribe_columns)

            with engine.connect() as connection:
                revision = MigrationContext.configure(connection).get_current_revision()
            self.assertEqual(revision, "20260718_0003")
            self.assertFalse((database_path.parent / "backups").exists())
            engine.dispose()

    def test_legacy_database_is_backed_up_and_upgraded_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "database.db"
            with sqlite3.connect(database_path) as connection:
                connection.executescript(
                    """
                    CREATE TABLE actor_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        birthday VARCHAR(20),
                        height VARCHAR(10),
                        bust VARCHAR(10),
                        waist VARCHAR(10),
                        hip VARCHAR(10),
                        cup VARCHAR(10),
                        hobby VARCHAR,
                        prefectures VARCHAR(50),
                        blood_type VARCHAR(5),
                        aliases JSON,
                        avatar_url VARCHAR,
                        social_media JSON,
                        ruby VARCHAR(100)
                    );
                    CREATE TABLE actor_subscribe (
                        actor_id INTEGER PRIMARY KEY,
                        is_subscribe BOOLEAN NOT NULL,
                        is_collect BOOLEAN NOT NULL,
                        created_at DATETIME,
                        FOREIGN KEY(actor_id) REFERENCES actor_data(id)
                    );
                    INSERT INTO actor_data (id, name) VALUES (1, 'legacy actor');
                    INSERT INTO actor_subscribe (
                        actor_id, is_subscribe, is_collect, created_at
                    ) VALUES (1, 1, 0, CURRENT_TIMESTAMP);
                    """
                )

            engine = self._engine(database_path)
            run_database_migrations(engine, database_path)

            inspector = inspect(engine)
            actor_columns = {
                column["name"] for column in inspector.get_columns("actor_data")
            }
            subscribe_columns = {
                column["name"]
                for column in inspector.get_columns("actor_subscribe")
            }
            self.assertIn("updated_at", actor_columns)
            self.assertIn("subscribe_order", subscribe_columns)
            self.assertIn("collect_order", subscribe_columns)
            movie_subscribe_columns = {
                column["name"]
                for column in inspector.get_columns("movie_subscribe")
            }
            self.assertIn("rule_config", movie_subscribe_columns)

            with engine.connect() as connection:
                actor_name = connection.execute(
                    text("SELECT name FROM actor_data WHERE id = 1")
                ).scalar_one()
                revision = MigrationContext.configure(connection).get_current_revision()
            self.assertEqual(actor_name, "legacy actor")
            self.assertEqual(revision, "20260718_0003")

            backups = list((database_path.parent / "backups").glob("*.db"))
            self.assertEqual(len(backups), 1)
            run_database_migrations(engine, database_path)
            self.assertEqual(
                len(list((database_path.parent / "backups").glob("*.db"))),
                1,
            )
            engine.dispose()

    def test_sqlite_connection_pragmas_are_enabled(self):
        connection = sqlite3.connect(":memory:")
        try:
            configure_sqlite_connection(connection)
            foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
            busy_timeout = connection.execute("PRAGMA busy_timeout").fetchone()[0]
            synchronous = connection.execute("PRAGMA synchronous").fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(foreign_keys, 1)
        self.assertEqual(busy_timeout, 5000)
        self.assertEqual(synchronous, 1)


if __name__ == "__main__":
    unittest.main()
