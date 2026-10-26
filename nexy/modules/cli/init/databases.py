"""The databases a new project can start with, and what each ORM needs to talk to them."""

from __future__ import annotations

# (key, label shown in the prompt). `other` asks for a URL; no database is the "no ORM" answer.
DATABASES: list[tuple[str, str]] = [
    ("sqlite", "SQLite"),
    ("postgresql", "PostgreSQL"),
    ("neon", "Neon (serverless PostgreSQL)"),
    ("mysql", "MySQL / MariaDB"),
    ("other", "Other"),
]

_TORTOISE = "Tortoise-ORM"
_FAMILY = {"postgresql": "postgresql", "neon": "postgresql", "mysql": "mysql"}
_NEON_HOST = "ep-xxx.region.aws.neon.tech"

# SQLAlchemy and SQLModel name the driver in the URL; Tortoise has its own schemes and drivers.
_SQL_URLS = {
    "postgresql": "postgresql+psycopg://user:password@localhost:5432/mydb",
    "mysql": "mysql+pymysql://user:password@localhost:3306/mydb",
}
_TORTOISE_URLS = {
    "postgresql": "postgres://user:password@localhost:5432/mydb",
    "mysql": "mysql://user:password@localhost:3306/mydb",
}
_DRIVERS = {
    False: {"postgresql": ["psycopg[binary]"], "mysql": ["pymysql"]},
    True: {"postgresql": ["asyncpg"], "mysql": ["aiomysql"]},
}


def default_url(database: str, orm: str) -> str:
    """The URL suggested for `database` with `orm` (empty when there is nothing to suggest)."""
    if database == "sqlite":
        return "sqlite:///dev.db"
    family = _FAMILY.get(database)
    if family is None:
        return ""
    urls = _TORTOISE_URLS if orm == _TORTOISE else _SQL_URLS
    url = urls[family]
    if database == "neon":
        url = url.replace("user:password@localhost:5432", f"user:password@{_NEON_HOST}")
        url += "?sslmode=require"
    return url


def driver_packages(database: str, orm: str) -> list[str]:
    """Python packages the ORM needs to reach `database` (SQLite ships with Python)."""
    family = _FAMILY.get(database)
    if family is None:
        return []
    return list(_DRIVERS[orm == _TORTOISE][family])
