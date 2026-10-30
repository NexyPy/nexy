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


class TestPurgeForgetsOrmTables:
    """SQLModel keeps its tables in one global registry that the purge does not touch.

    A re-import of `class User(SQLModel, table=True)` then fails with "Table 'user' is already
    defined for this MetaData instance", and every module that imports the model fails with it.
    """

    @staticmethod
    def _sqlmodel(monkeypatch):
        import sys
        import types

        from sqlalchemy.orm import registry

        shared = registry()
        base = types.SimpleNamespace(metadata=shared.metadata, _sa_registry=shared)
        monkeypatch.setitem(sys.modules, "sqlmodel", types.SimpleNamespace(SQLModel=base))
        return shared

    @staticmethod
    def _declare(shared):
        from sqlalchemy import Column, Integer, Table

        Table("usermodel", shared.metadata, Column("id", Integer, primary_key=True))

    def test_a_table_can_be_declared_again_after_the_purge(self, tmp_path, monkeypatch):
        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        shared = self._sqlmodel(monkeypatch)
        self._declare(shared)

        purge_project_modules(root=tmp_path)

        self._declare(shared)
        assert list(shared.metadata.tables) == ["usermodel"]

    def test_the_purge_does_not_import_sqlmodel_when_the_project_has_none(
        self, tmp_path, monkeypatch
    ):
        import sys

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        monkeypatch.delitem(sys.modules, "sqlmodel", raising=False)

        purge_project_modules(root=tmp_path)

        assert "sqlmodel" not in sys.modules


class TestPurgeForgetsActions:
    """`ACTIONS_STORE` lives in the framework: purging modules must forget their actions.

    Dropping the modules is not enough — a re-import overwrites its own entries, but an
    action whose module is gone would keep its endpoint and its line in `actions.ts`.
    """

    @staticmethod
    def _register(monkeypatch, name: str, file: Path) -> None:
        import sys
        import types

        module = types.ModuleType(name)
        module.__file__ = str(file)
        monkeypatch.setitem(sys.modules, name, module)

    def test_the_store_forgets_the_actions_of_a_purged_module(self, tmp_path, monkeypatch):
        from nexy.modules.cli.devtools.watch.purge import purge_project_modules
        from nexy.modules.routers.actions.store import ACTIONS_STORE

        source = tmp_path / "stale_actions.py"
        source.write_text("")
        self._register(monkeypatch, "stale_actions", source)
        ACTIONS_STORE.registry["stale_actions.run"] = lambda: 1
        ACTIONS_STORE.path_map["stale_actions.run"] = "/_nx_deadbeef"
        try:
            purge_project_modules(root=tmp_path)
            assert "stale_actions.run" not in ACTIONS_STORE.registry
            assert "stale_actions.run" not in ACTIONS_STORE.path_map
        finally:
            ACTIONS_STORE.registry.pop("stale_actions.run", None)
            ACTIONS_STORE.path_map.pop("stale_actions.run", None)

    def test_an_action_of_a_module_that_was_not_purged_stays(self, tmp_path):
        from nexy.modules.cli.devtools.watch.purge import purge_project_modules
        from nexy.modules.routers.actions.store import ACTIONS_STORE

        ACTIONS_STORE.registry["src.services.api.create"] = lambda: 1
        try:
            purge_project_modules(root=tmp_path)
            assert "src.services.api.create" in ACTIONS_STORE.registry
        finally:
            ACTIONS_STORE.registry.pop("src.services.api.create", None)


class TestPurgeDropsBytecode:
    """A ``.pyc`` records its source with one-second granularity: a file saved twice in
    the same second with the same size would be re-imported from the stale cache."""

    @staticmethod
    def _register(monkeypatch, name: str, file: Path) -> None:
        import sys
        import types

        module = types.ModuleType(name)
        module.__file__ = str(file)
        monkeypatch.setitem(sys.modules, name, module)

    def test_the_purge_deletes_the_cached_bytecode_of_a_purged_module(
        self, tmp_path, monkeypatch
    ):
        from importlib.util import cache_from_source

        from nexy.modules.cli.devtools.watch.purge import purge_project_modules

        source = tmp_path / "stale_source.py"
        source.write_text("VALUE = 1\n")
        self._register(monkeypatch, "stale_source", source)
        cache = Path(cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text("stale", encoding="utf-8")

        purge_project_modules(root=tmp_path)

        assert not cache.exists()


class TestPurgeReloadsConfig:
    """A restart must re-read nexyconfig.py: Config is a class attribute living outside
    `sys.modules`, so a purge alone never applies an edited configuration."""

    @staticmethod
    def _write(tmp_path: Path, body: str) -> None:
        (tmp_path / "nexyconfig.py").write_text(body, encoding="utf-8")

    @staticmethod
    def _forget(monkeypatch, tmp_path: Path, body: str) -> None:
        import importlib
        import sys

        monkeypatch.syspath_prepend(str(tmp_path))
        TestPurgeReloadsConfig._write(tmp_path, body)
        monkeypatch.delitem(sys.modules, "nexyconfig", raising=False)
        importlib.invalidate_caches()

    def test_a_changed_setting_is_visible_after_a_reload(self, tmp_path, monkeypatch):
        import sys

        from nexy.core.config import Config

        self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = 'Old'\n")
        try:
            Config.reset()
            Config()
            assert Config.TOC_TITLE == "Old"

            self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = 'New'\n")
            Config.reset()
            Config()

            assert Config.TOC_TITLE == "New"
        finally:
            sys.modules.pop("nexyconfig", None)
            Config.reset()

    def test_a_setting_the_new_config_drops_returns_to_its_default(
        self, tmp_path, monkeypatch
    ):
        import sys

        from nexy.core.config import Config

        self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = 'Old'\n")
        try:
            Config.reset()
            Config()
            assert Config.TOC_TITLE == "Old"

            # The new file no longer derives a title: the default comes back.
            self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = ''\n")
            Config.reset()
            Config()

            assert Config.TOC_TITLE == "Table of Contents"
        finally:
            sys.modules.pop("nexyconfig", None)
            Config.reset()

    def test_a_restart_applies_the_edited_nexyconfig(self, tmp_path, monkeypatch):
        """`_purge_app_modules` is what a dev restart runs before importing the app again."""
        import sys

        from nexy.core.config import Config
        from nexy.modules.cli.commands.dev import _purge_app_modules

        self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = 'Old'\n")
        monkeypatch.chdir(tmp_path)
        try:
            Config.reset()
            Config()
            assert Config.TOC_TITLE == "Old"

            self._forget(monkeypatch, tmp_path, "class NexyConfig:\n    useTocTitle = 'New'\n")
            _purge_app_modules()
            Config()

            assert Config.TOC_TITLE == "New"
        finally:
            sys.modules.pop("nexyconfig", None)
            Config.reset()
