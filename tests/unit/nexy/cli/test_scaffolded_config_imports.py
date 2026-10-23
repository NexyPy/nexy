"""A freshly scaffolded config must import and expose its framework.

This guards the quickstart: `nexy init` renders ``nexyconfig.py`` from a
template, and that file is the first thing a new project executes. If its
import path does not resolve, the project cannot start.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

from nexy.modules.cli.constants import TEMPLATES_DIR
from nexy.modules.cli.init.template_setup import _render_local_template

TEMPLATES = (
    ("web-fbr", "react", "FBRouter"),
    ("web-modular", "react", "modular"),
)


def _stub_src() -> None:
    """Fabricate the project-local ``src`` package a template imports."""
    if "src" in sys.modules:
        return
    for name in (
        "src",
        "src.apps",
        "src.apps.app_module",
        "src.apps.home",
        "src.apps.home.app_module",
    ):
        module = types.ModuleType(name)
        module.__path__ = []
        if name.endswith("app_module"):
            module.AppModule = type("AppModule", (), {})
        sys.modules[name] = module


def _load(path: Path, name: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("template", "framework", "_kind"), TEMPLATES)
def test_scaffolded_config_imports(tmp_path: Path, template: str, framework: str, _kind: str):
    _stub_src()
    config = {
        "client_framework": framework,
        "FBRouter": _kind == "FBRouter",
        "project_type": "web",
    }

    _render_local_template(template, tmp_path, config, "demo")

    module = _load(tmp_path / "nexyconfig.py", f"_cfg_{template}")
    instance = module.NexyConfig()
    name = instance.useFF[0].name if isinstance(instance.useFF, list) else instance.useFF.name
    assert name == framework


def test_render_local_template_exists_in_bundled_templates():
    assert (TEMPLATES_DIR / "web-fbr").is_dir()
