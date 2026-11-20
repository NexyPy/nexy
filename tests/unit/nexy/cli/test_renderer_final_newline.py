"""Every file `nx new` writes from a template ends with exactly one newline.

Jinja2 drops the last newline of a template, so a project got `pyproject.toml` and
`src/actions/__init__.py` with none, which `cat` and `ruff` (W292) both trip on.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.modules.cli.init.renderer import TemplateRenderer


def _rendered(tmp_path: Path, template: str) -> str:
    src = tmp_path / "src"
    src.mkdir()
    (src / "file.txt.jinja2").write_text(template, encoding="utf-8")
    TemplateRenderer(src, tmp_path / "out", {}).render()
    return (tmp_path / "out" / "file.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("template", ["last line\n", "last line", "last line\n\n\n"])
def test_a_rendered_file_ends_with_one_newline(tmp_path, template):
    assert _rendered(tmp_path, template) == "last line\n"


def test_the_starter_pyproject_ends_with_one_newline(tmp_path):
    from nexy.modules.cli.constants import TEMPLATES_DIR

    source = (TEMPLATES_DIR / "_shared" / "web" / "pyproject.toml.jinja2").read_text("utf-8")
    assert _rendered(tmp_path, source).endswith('">=3.12"\n')
