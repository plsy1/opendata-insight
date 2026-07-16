import unittest

from sqlalchemy import create_engine, inspect, text

from database.base import _migrate_actor_updated_at


class DatabaseMigrationTests(unittest.TestCase):
    def test_actor_updated_at_column_is_added_idempotently(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE actor_data (id INTEGER PRIMARY KEY, name VARCHAR)")
            )

        _migrate_actor_updated_at(engine)
        _migrate_actor_updated_at(engine)

        columns = {
            column["name"] for column in inspect(engine).get_columns("actor_data")
        }
        self.assertIn("updated_at", columns)


if __name__ == "__main__":
    unittest.main()
