"""The database of the shop: SQLite in `store.db` unless DATABASE_URL says otherwise."""

import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///store.db"))


def create_tables() -> None:
    """Create the tables of every imported model that does not exist yet."""
    import src.models.order  # noqa: F401 - the tables to create are those of imported models

    SQLModel.metadata.create_all(engine)
