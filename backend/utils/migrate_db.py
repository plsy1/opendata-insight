from app_paths import DATABASE_PATH
from database import init_database


def migrate() -> None:
    print(f"Migrating database at {DATABASE_PATH}...")
    init_database()
    print("Database is up to date.")

if __name__ == "__main__":
    migrate()
