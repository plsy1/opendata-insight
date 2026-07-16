import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

main_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
database_path = os.path.join(main_dir, "data", "database.db")
DATABASE_URL = f"sqlite:///{database_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    import database.models

    Base.metadata.create_all(bind=engine)
    _migrate_actor_updated_at()


def _migrate_actor_updated_at(target_engine=engine):
    inspector = inspect(target_engine)
    if "actor_data" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("actor_data")}
    if "updated_at" in columns:
        return

    with target_engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE actor_data ADD COLUMN updated_at DATETIME")
        )
