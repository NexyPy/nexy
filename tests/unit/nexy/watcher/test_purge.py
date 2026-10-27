"""A dev restart imports the project again: the purge drops what it must, keeps the rest."""

from pathlib import Path


class TestPurgeProjectModules:
    @staticmethod
    def _register(name: str, file: Path, monkeypatch):
        import sys
        import types

        module = types.ModuleType(name)
        module.__file__ = str(file)
        monkeypatch.setitem(sys.modules, name, module)

    def test_purge_removes_project_module(self, tmp_path, monkeypatch):
        import sys

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        source = tmp_path / "proj_probe.py"
        source.write_text("")
        self._register("proj_purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "proj_purge_probe" not in sys.modules

    def test_purge_reports_removed_names(self, tmp_path, monkeypatch):
        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        source = tmp_path / "reported_probe.py"
        source.write_text("")
        self._register("reported_purge_probe", source, monkeypatch)

        purged = purge_project_modules(root=tmp_path)

        assert "reported_purge_probe" in purged

    def test_purge_keeps_framework_module(self, tmp_path, monkeypatch):
        import sys

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        source = tmp_path / "framework_probe.py"
        source.write_text("")
        self._register("nexy._purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "nexy._purge_probe" in sys.modules

    def test_purge_keeps_venv_module(self, tmp_path, monkeypatch):
        import sys

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        site = tmp_path / ".venv" / "lib"
        site.mkdir(parents=True)
        source = site / "env_probe.py"
        source.write_text("")
        self._register("venv_purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "venv_purge_probe" in sys.modules


class TestPurgeKeepsNamespacePackagesConsistent:
    """`src/routes` has no __init__.py: purging `src` without `src.routes` breaks imports."""

    def _project(self, tmp_path, monkeypatch):
        import importlib
        import sys

        package = tmp_path / "purgeproj"
        (package / "routes").mkdir(parents=True)
        (package / "__init__.py").write_text("")
        (package / "routes" / "users.py").write_text("VALUE = 1\n")
        monkeypatch.syspath_prepend(str(tmp_path))
        importlib.invalidate_caches()
        importlib.import_module("purgeproj.routes.users")
        return sys

    def test_a_route_can_be_imported_again_after_a_purge(self, tmp_path, monkeypatch):
        import importlib

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        sys = self._project(tmp_path, monkeypatch)
        try:
            purge_project_modules(root=tmp_path)
            module = importlib.import_module("purgeproj.routes.users")
            assert module.VALUE == 1
        finally:
            for name in [n for n in sys.modules if n.startswith("purgeproj")]:
                del sys.modules[name]

    def test_the_namespace_package_is_purged_with_its_parent(self, tmp_path, monkeypatch):
        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        sys = self._project(tmp_path, monkeypatch)
        try:
            purged = purge_project_modules(root=tmp_path)
            assert "purgeproj.routes" in purged
        finally:
            for name in [n for n in sys.modules if n.startswith("purgeproj")]:
                del sys.modules[name]
