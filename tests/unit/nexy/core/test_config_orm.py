"""`useORM`: the ORM a project was made with, so commands such as `nx migrate` need not guess it."""

from __future__ import annotations

from nexy.core.config import Config


def test_use_orm_is_read_from_the_project_config(nexy_project):
    nexy_project('useORM = "SQLAlchemy"')
    assert Config().useORM == "SQLAlchemy"


def test_use_orm_is_none_when_the_project_names_none(nexy_project):
    nexy_project()
    assert Config().useORM is None
