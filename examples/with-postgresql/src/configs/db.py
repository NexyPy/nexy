"""The connection: DATABASE_URL picks the database, the code does not change.

postgresql+psycopg://user:password@host:5432/name    PostgreSQL, with psycopg 3
sqlite:///dev.db                                       SQLite, when DATABASE_URL is unset
"""

import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
# pool_pre_ping: a connection the server closed (a restart, an idle timeout) is replaced, not used.
engine = create_engine(URL, pool_pre_ping=True)


def create_tables() -> None:
    """Create the tables that do not exist yet. A real project moves to migrations (Alembic) once
    a table changes: see docs/guides/databases.md."""
    import src.models  # noqa: F401  every model must be imported before create_all

    SQLModel.metadata.create_all(engine)
