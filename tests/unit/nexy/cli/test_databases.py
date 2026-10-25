"""The databases `nx new` offers, their default URLs and the driver each ORM needs."""

from __future__ import annotations

import pytest

from nexy.modules.cli.init.databases import DATABASES, default_url, driver_packages


def test_the_offered_databases():
    assert [key for key, _ in DATABASES] == [
        "sqlite",
        "postgresql",
        "neon",
        "mysql",
        "other",
        "none",
    ]


@pytest.mark.parametrize(
    ("database", "orm", "url"),
    [
        ("sqlite", "SQLModel", "sqlite:///dev.db"),
        ("postgresql", "SQLAlchemy", "postgresql+psycopg://user:password@localhost:5432/mydb"),
        ("mysql", "SQLModel", "mysql+pymysql://user:password@localhost:3306/mydb"),
        ("postgresql", "Tortoise-ORM", "postgres://user:password@localhost:5432/mydb"),
        ("mysql", "Tortoise-ORM", "mysql://user:password@localhost:3306/mydb"),
    ],
)
def test_default_url_follows_the_orm_dialect(database, orm, url):
    assert default_url(database, orm) == url


def test_neon_url_requires_ssl():
    assert default_url("neon", "SQLModel").endswith(".neon.tech/mydb?sslmode=require")


def test_other_database_has_no_default_url():
    assert default_url("other", "SQLModel") == ""


@pytest.mark.parametrize(
    ("database", "orm", "packages"),
    [
        ("sqlite", "SQLModel", []),
        ("postgresql", "SQLModel", ["psycopg[binary]"]),
        ("neon", "SQLAlchemy", ["psycopg[binary]"]),
        ("mysql", "SQLAlchemy", ["pymysql"]),
        ("postgresql", "Tortoise-ORM", ["asyncpg"]),
        ("mysql", "Tortoise-ORM", ["aiomysql"]),
        ("other", "SQLModel", []),
    ],
)
def test_driver_packages(database, orm, packages):
    assert driver_packages(database, orm) == packages
