import os
import sys
from sqlalchemy import create_engine
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
