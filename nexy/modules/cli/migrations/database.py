"""The database of a project: where its URL is written, and whether it answers."""

from __future__ import annotations

import os
from pathlib import Path


def database_url(project: Path) -> str | None:
    """`DATABASE_URL` from the project's `.env` (when python-dotenv is there) or the environment."""
    env_file = project / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
        except ImportError:
            pass
    return os.getenv("DATABASE_URL")


def connection_problem(url: str) -> tuple[str, Exception] | None:
    """("driver" | "connection", error) when *url* cannot be used, else None."""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
    except ImportError as error:
        return "driver", error
    except Exception as error:
        return "connection", error
    return None
