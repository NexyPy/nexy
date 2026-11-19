"""A project with an ORM renders with the Python packages it needs, for its pyproject.toml."""

from __future__ import annotations

from nexy.modules.cli.init.template_setup import _template_context


def test_an_orm_project_renders_with_its_packages():
    context = _template_context({"orm": "SQLModel", "database": "sqlite"}, "shop")
    assert context["python_packages"] == ["sqlmodel", "alembic", "python-dotenv"]


def test_a_project_without_an_orm_renders_with_no_package():
    assert _template_context({"orm": "None"}, "shop")["python_packages"] == []
