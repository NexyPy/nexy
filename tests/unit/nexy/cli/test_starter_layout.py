"""A file-based starter keeps its routes in `src/routes/`, and nowhere else."""

from __future__ import annotations

import pytest

from nexy.modules.cli.init.registry import GITHUB_TEMPLATES
from nexy.modules.cli.init.resolver import TemplateResolver
from nexy.modules.cli.init.template_setup import _render_local_template

FILE_BASED = sorted(name for name in GITHUB_TEMPLATES if "-fbr" in name)


@pytest.mark.parametrize("name", FILE_BASED)
def test_a_file_based_starter_writes_no_nested_src_folder(name, tmp_path) -> None:
    config = {**TemplateResolver.config_for(name), "agents": False}
    _render_local_template(TemplateResolver.resolve(config), tmp_path, config, "demo")
    assert not (tmp_path / "src" / "src").exists()
