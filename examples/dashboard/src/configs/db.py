"""The database of the app: SQLite in `dashboard.db` unless DATABASE_URL says otherwise."""

import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dashboard.db"))


def create_tables() -> None:
    """Create the tables of every imported model that does not exist yet."""
    SQLModel.metadata.create_all(engine)
