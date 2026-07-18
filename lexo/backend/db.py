from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from config import settings

# Neon pooled URL includes ?sslmode=require; psycopg2 honors it via the DSN.
engine = create_engine(settings.database_url, pool_pre_ping=True)


def create_db_and_tables() -> None:
    # Register all table models on SQLModel.metadata before create_all.
    from models import tables as _tables  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
