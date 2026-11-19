"""A new project asks for at least the Nexy release that created it."""

from __future__ import annotations

from pathlib import Path

from nexy.__version__ import __version__
from nexy.modules.cli.constants import TEMPLATES_DIR
from nexy.modules.cli.init.renderer import TemplateRenderer


def _pyproject(kind: str, dest: Path) -> str:
    src = dest / "src"
    src.mkdir(parents=True)
    template = (TEMPLATES_DIR / "_shared" / kind / "pyproject.toml.jinja2").read_text("utf-8")
    (src / "pyproject.toml.jinja2").write_text(template, encoding="utf-8")
    TemplateRenderer(src, dest / "out", {"project_name": "demo"}).render()
    return (dest / "out" / "pyproject.toml").read_text("utf-8")


def test_a_web_project_asks_for_the_release_that_made_it(tmp_path):
    assert f'"nexy>={__version__}"' in _pyproject("web", tmp_path)


def test_an_api_project_asks_for_the_release_that_made_it(tmp_path):
    assert f'"nexy>={__version__}"' in _pyproject("api", tmp_path)
