import sys
from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.modules.routers.fbrouter.dependencies import RouteDependencies


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(Config, "ROUTER_PATH", str(tmp_path / "src" / "routes"))
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "routes").mkdir()
    (tmp_path / "src" / "routes" / "__init__.py").write_text("", encoding="utf-8")
    yield tmp_path
    for name in list(sys.modules):
        if name.split(".")[0] == "src":
            del sys.modules[name]


def test_collect_returns_module_dependencies(project: Path) -> None:
    (project / "src" / "routes" / "dependencies.py").write_text(
        "def guard():\n    return None\n\ndependencies = [guard, 'not callable']\n",
        encoding="utf-8",
    )
    deps = RouteDependencies.collect(str(project / "src" / "routes" / "page.nexy"))
    assert [dep.__name__ for dep in deps] == ["guard"]


def test_collect_without_dependencies_file_returns_empty(project: Path) -> None:
    assert RouteDependencies.collect(str(project / "src" / "routes" / "page.nexy")) == []


def test_collect_survives_unimportable_dependencies_module(project: Path) -> None:
    (project / "src" / "routes" / "dependencies.py").write_text(
        "import missing_package_xyz\n", encoding="utf-8"
    )
    assert RouteDependencies.collect(str(project / "src" / "routes" / "page.nexy")) == []


def test_collect_outside_router_root_returns_empty(project: Path) -> None:
    outside = project / "elsewhere"
    outside.mkdir()
    assert RouteDependencies.collect(str(outside / "page.nexy")) == []
