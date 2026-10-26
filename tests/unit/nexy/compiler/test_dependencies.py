"""A component is compiled after the components it imports, each of them once."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.dependencies import (
    _compiled_module,
    _imported_components,
    compile_dependencies,
    resolve_dependency,
)


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(Config, "ALIASES", {"@": "src/"})
    VFS().clear()
    yield tmp_path
    VFS().clear()


def _write(root: Path, name: str, text: str = "") -> str:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return name


class TestResolve:
    def test_a_relative_import_is_relative_to_the_project(self, project):
        _write(project, "src/a.nexy")
        assert resolve_dependency("src/a.nexy", "./card.nexy") == "src/card.nexy"

    def test_a_parent_import_climbs(self, project):
        assert resolve_dependency("src/pages/a.nexy", "../ui/card.nexy") == "src/ui/card.nexy"

    def test_an_alias_is_replaced(self, project):
        assert resolve_dependency("src/a.nexy", "@/ui/card.nexy") == "src/ui/card.nexy"

    @pytest.mark.usefixtures("project")
    def test_a_package_import_is_not_a_dependency(self):
        assert resolve_dependency("src/a.nexy", "fastapi") is None

    def test_a_relative_import_outside_the_project_is_not_a_dependency(self, project):
        assert resolve_dependency("src/a.nexy", "../../../../elsewhere/x.nexy") is None


class TestImportedComponents:
    def test_each_nexy_import_is_listed(self, project):
        source = 'from "./a.nexy" import A\nfrom "./b.nexy" import B\n'
        assert list(_imported_components("src/page.nexy", source)) == ["src/a.nexy", "src/b.nexy"]

    def test_other_files_are_not_components(self, project):
        assert list(_imported_components("src/p.nexy", 'from "./card.tsx" import C\n')) == []

    def test_an_import_inside_a_code_fence_is_an_example(self, project):
        source = '```python\nfrom "./a.nexy" import A\n```\n'
        assert list(_imported_components("src/page.nexy", source)) == []


class TestCompileDependencies:
    def test_the_dependency_is_compiled_before_the_page_returns(self, project):
        _write(project, "src/page.nexy", 'from "./card.nexy" import Card\n')
        _write(project, "src/card.nexy")
        compiled: list[str] = []
        compile_dependencies("src/page.nexy", compiled.append)
        assert compiled == ["src/card.nexy"]

    def test_dependencies_of_dependencies_come_first(self, project):
        _write(project, "src/page.nexy", 'from "./a.nexy" import A\n')
        _write(project, "src/a.nexy", 'from "./b.nexy" import B\n')
        _write(project, "src/b.nexy")
        compiled: list[str] = []
        compile_dependencies("src/page.nexy", compiled.append)
        assert compiled == ["src/b.nexy", "src/a.nexy"]

    def test_a_cycle_does_not_loop(self, project):
        _write(project, "src/a.nexy", 'from "./b.nexy" import B\n')
        _write(project, "src/b.nexy", 'from "./a.nexy" import A\n')
        compiled: list[str] = []
        compile_dependencies("src/a.nexy", compiled.append)
        assert sorted(compiled) == ["src/a.nexy", "src/b.nexy"]

    def test_a_dependency_that_is_already_compiled_is_left_alone(self, project):
        _write(project, "src/page.nexy", 'from "./card.nexy" import Card\n')
        VFS().write(_compiled_module("src/card.nexy"), "x = 1")
        compiled: list[str] = []
        compile_dependencies("src/page.nexy", compiled.append)
        assert compiled == []

    def test_a_framework_route_has_no_component_dependencies(self, project):
        _write(project, "src/page.tsx", 'from "./card.nexy" import Card\n')
        compiled: list[str] = []
        compile_dependencies("src/page.tsx", compiled.append)
        assert compiled == []

    @pytest.mark.usefixtures("project")
    def test_a_missing_file_is_not_an_error(self):
        compile_dependencies("src/gone.nexy", lambda _path: None)
