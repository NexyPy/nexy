"""A new project lists the packages of its ORM in pyproject.toml, so one `uv sync` installs them."""

from __future__ import annotations

import tomllib
from pathlib import Path

from nexy.modules.cli.constants import TEMPLATES_DIR
from nexy.modules.cli.init.renderer import TemplateRenderer

PACKAGES = ["sqlmodel", "alembic", "python-dotenv"]


def _dependencies(kind: str, dest: Path, packages: list[str]) -> list[str]:
    src = dest / "src"
    src.mkdir(parents=True)
    template = (TEMPLATES_DIR / "_shared" / kind / "pyproject.toml.jinja2").read_text("utf-8")
    (src / "pyproject.toml.jinja2").write_text(template, encoding="utf-8")
    context = {"project_name": "demo", "python_packages": packages}
    TemplateRenderer(src, dest / "out", context).render()
    text = (dest / "out" / "pyproject.toml").read_text("utf-8")
    return tomllib.loads(text)["project"]["dependencies"][1:]


def test_a_web_project_lists_the_packages_of_its_orm(tmp_path):
    assert _dependencies("web", tmp_path, PACKAGES) == PACKAGES


def test_a_web_project_without_an_orm_lists_only_nexy(tmp_path):
    assert _dependencies("web", tmp_path, []) == []


def test_an_api_project_lists_the_packages_of_its_orm(tmp_path):
    assert _dependencies("api", tmp_path, PACKAGES) == PACKAGES
