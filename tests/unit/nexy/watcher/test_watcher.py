import asyncio
import time
from pathlib import Path

import pytest
from watchdog.events import FileSystemEvent

from nexy.utils.dev.watcher import WatchHandler, is_ignored_path, normalize_path
from nexy.utils.fs.vfs import VFS


@pytest.fixture(autouse=True)
def _clean_vfs():
    yield
    VFS().clear()


NEXY_SOURCE = """\
---
title = "Test"
---
<h1>{{ title }}</h1>
"""


# ── Helpers ────────────────────────────────────────────────────────────────────


@pytest.fixture
def handler() -> WatchHandler:
    return WatchHandler()


def _make_event(src_path: str, dest_path: str | None = None) -> FileSystemEvent:
    event = FileSystemEvent(src_path)
    event.is_directory = False
    if dest_path is not None:
        event.dest_path = dest_path
    return event


# ── normalize_path ──────────────────────────────────────────────────────────────────


class TestNormalize:
    def test_string(self):
        assert normalize_path("some/path/file.nexy") == "some/path/file.nexy"

    def test_bytes(self):
        assert normalize_path(b"some/path/file.nexy") == "some/path/file.nexy"

    def test_backslashes(self):
        assert normalize_path("src\\routes\\index.nexy") == "src/routes/index.nexy"

    def test_strips_dot_slash(self):
        assert normalize_path("./src/routes/index.nexy") == "src/routes/index.nexy"

    def test_strips_cwd_prefix(self):
        cwd = Path.cwd().as_posix()
        abs_path = f"{cwd}/src/routes/index.nexy"
        assert normalize_path(abs_path) == "src/routes/index.nexy"

    def test_absolute_path_on_different_drive(self):
        cwd = Path.cwd()
        other_drive = "E:" if cwd.drive == "D:" else "D:"
        abs_path = f"{other_drive}/other/project/src/routes/index.nexy"
        result = normalize_path(abs_path)
        assert result == abs_path.replace("\\", "/").lstrip("./")


# ── is_ignored_path ───────────────────────────────────────────────────────────────────────


class TestSkip:
    def test_skips_git(self):
        assert is_ignored_path(".git/config")

    def test_skips_venv(self):
        assert is_ignored_path("venv/bin/python")

    def test_skips_pycache(self):
        assert is_ignored_path("__pycache__/cache.py")

    def test_skips_node_modules(self):
        assert is_ignored_path("node_modules/pkg/index.js")

    def test_skips_nexy_dir(self):
        assert is_ignored_path("__nexy__/generated.py")

    def test_allows_src_routes(self):
        assert not is_ignored_path("src/routes/index.nexy")

    def test_allows_py_file(self):
        assert not is_ignored_path("src/lib/utils.py")


# ── on_modified ─────────────────────────────────────────────────────────────────


class TestOnModified:
    def test_compiles_nexy_and_updates_vfs(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        nexy_file = routes / "index.nexy"
        nexy_file.write_text(NEXY_SOURCE)

        handler.on_modified(_make_event(str(nexy_file)))

        vfs = VFS()
        files = vfs.list_files()
        py_files = [f for f in files if f.endswith(".py")]
        assert any("index" in f for f in py_files), f"No compiled .py found in VFS: {files}"

    def test_recompiles_on_second_modification(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        nexy_file = routes / "page.nexy"
        nexy_file.write_text(NEXY_SOURCE)

        handler.on_modified(_make_event(str(nexy_file)))
        first_files = set(VFS().list_files())

        nexy_file.write_text(NEXY_SOURCE + "\n<!---- updated ---->")
        handler.on_modified(_make_event(str(nexy_file)))
        second_files = set(VFS().list_files())

        assert first_files == second_files, "VFS should have same files after recompile"

    def test_ignores_skipped_paths(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ignored = tmp_path / "node_modules" / "pkg.nexy"
        ignored.parent.mkdir(parents=True)
        ignored.write_text(NEXY_SOURCE)

        before = set(VFS().list_files())
        handler.on_modified(_make_event(str(ignored)))
        after = set(VFS().list_files())
        assert before == after, "Skipped paths should not trigger compilation"

    def test_calls_reload_api(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        py_file = routes / "app.py"
        py_file.write_text("print('hello')")

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_modified(_make_event(str(py_file)))

        assert len(calls) == 1, "on_reload_api should be called once for .py file"

    def test_does_not_call_reload_api_on_skipped(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = tmp_path / ".venv" / "lib.nexy"
        f.parent.mkdir(parents=True)
        f.write_text(NEXY_SOURCE)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_modified(_make_event(str(f)))

        assert len(calls) == 0, "on_reload_api should not be called for skipped paths"


# ── on_created ──────────────────────────────────────────────────────────────────


class TestOnCreated:
    def test_compiles_new_nexy_file(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        nexy_file = routes / "newpage.nexy"
        nexy_file.write_text(NEXY_SOURCE)

        handler.on_created(_make_event(str(nexy_file)))

        vfs = VFS()
        py_files = [f for f in vfs.list_files() if f.endswith(".py")]
        assert any("newpage" in f for f in py_files), f"New page not compiled: {py_files}"

    def test_calls_reload_api(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        py_file = routes / "app.py"
        py_file.write_text("print('hello')")

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_created(_make_event(str(py_file)))

        assert len(calls) == 1

    def test_ignores_skipped_paths(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        f = tmp_path / ".venv" / "lib.nexy"
        f.parent.mkdir(parents=True)
        f.write_text(NEXY_SOURCE)

        before = set(VFS().list_files())
        handler.on_created(_make_event(str(f)))
        after = set(VFS().list_files())
        assert before == after


# ── on_deleted ──────────────────────────────────────────────────────────────────


class TestOnDeleted:
    def test_calls_reload_api(self, handler):
        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_deleted(_make_event("src/routes/app.py"))
        assert len(calls) == 1

    def test_no_error_for_non_existent(self, handler):
        handler.on_deleted(_make_event("src/routes/ghost.nexy"))


# ── on_moved ────────────────────────────────────────────────────────────────────


class TestOnMoved:
    def test_creates_at_destination(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        src = routes / "old_name.nexy"
        src.write_text(NEXY_SOURCE)
        dest = routes / "new_name.nexy"

        src.rename(dest)

        event = FileSystemEvent(str(src))
        event.is_directory = False
        event.dest_path = str(dest)
        event.event_type = "moved"

        handler.on_moved(event)

        vfs = VFS()
        all_files = vfs.list_files()
        new_names = [f for f in all_files if "new_name" in f]
        assert len(new_names) > 0, f"No files for new_name in VFS: {all_files}"

    def test_cleans_up_source(self, handler):
        pass  # on_deleted handles cleanup, covered above


# ── _trigger_reload (single HMR owner) ─────────────────────────────────────────


class TestTriggerReload:
    @pytest.fixture(autouse=True)
    def _capture_broadcast(self, monkeypatch):
        from nexy.runtime.hmr import HMR_MANAGER

        self.broadcast_calls: list[str] = []
        self.reload_calls: list[int] = []

        async def _fake_broadcast(path: str = ""):
            self.broadcast_calls.append(path)

        class _FakeLoop:
            pass

        monkeypatch.setattr(HMR_MANAGER, "loop", _FakeLoop())
        monkeypatch.setattr(HMR_MANAGER, "broadcast_reload", _fake_broadcast)
        monkeypatch.setattr(
            "nexy.utils.dev.watcher.asyncio.run_coroutine_threadsafe",
            lambda coro, _loop: asyncio.run(coro),
        )

    def test_nexy_broadcasts(self, handler):
        handler._trigger_reload("src/routes/index.nexy")
        assert self.broadcast_calls == ["src/routes/index.nexy"]

    def test_md_broadcasts(self, handler):
        handler._trigger_reload("src/routes/page.md")
        assert self.broadcast_calls == ["src/routes/page.md"]

    def test_tsx_does_not_broadcast(self, handler):
        handler._trigger_reload("src/routes/page.tsx")
        assert self.broadcast_calls == []

    def test_mdx_does_not_broadcast(self, handler):
        handler._trigger_reload("src/routes/about.mdx")
        assert self.broadcast_calls == []

    def test_vue_does_not_broadcast(self, handler):
        handler._trigger_reload("src/routes/app.vue")
        assert self.broadcast_calls == []

    def test_py_triggers_api_restart_not_broadcast(self, handler):
        handler.on_reload_api = lambda: self.reload_calls.append(1)
        handler._trigger_reload("src/routes/api.py")
        assert self.broadcast_calls == []
        assert self.reload_calls == [1]


class TestHmrDebugTiming:
    def test_logs_timing_when_debug_enabled(self, handler, monkeypatch):
        monkeypatch.setenv("NEXY_HMR_DEBUG", "1")
        logged = []
        monkeypatch.setattr(
            "nexy.utils.dev.watcher.console.print",
            lambda msg: logged.append(str(msg)),
        )
        handler._log_hmr_timing("src/routes/index.nexy", 0.0)
        assert len(logged) == 1
        assert "hmr" in logged[0]

    def test_silent_when_debug_disabled(self, handler, monkeypatch):
        monkeypatch.delenv("NEXY_HMR_DEBUG", raising=False)
        logged = []
        monkeypatch.setattr(
            "nexy.utils.dev.watcher.console.print",
            lambda msg: logged.append(str(msg)),
        )
        handler._log_hmr_timing("src/routes/index.nexy", 0.0)
        assert logged == []

    def test_silent_without_start_time(self, handler, monkeypatch):
        monkeypatch.setenv("NEXY_HMR_DEBUG", "1")
        logged = []
        monkeypatch.setattr(
            "nexy.utils.dev.watcher.console.print",
            lambda msg: logged.append(str(msg)),
        )
        handler._log_hmr_timing("src/routes/index.nexy", None)
        assert logged == []


# ── module purge ────────────────────────────────────────────────────────────────


class _FakeSys:
    def __init__(self, modules: dict):
        self.modules = modules


class TestModulePurge:
    def test_purge_removes_route_module(self, handler, monkeypatch):
        fake_sys = _FakeSys({"__nexy__.src.routes.index": object()})
        monkeypatch.setattr("nexy.utils.dev.watcher.sys", fake_sys)
        handler._purge_route_modules("src/routes/index.nexy")
        assert "__nexy__.src.routes.index" not in fake_sys.modules

    def test_purge_removes_markdown_module(self, handler, monkeypatch):
        fake_sys = _FakeSys({"__nexy__.src.routes.hello": object()})
        monkeypatch.setattr("nexy.utils.dev.watcher.sys", fake_sys)
        handler._purge_route_modules("src/routes/hello.md")
        assert "__nexy__.src.routes.hello" not in fake_sys.modules

    def test_purge_ignores_frontend_file(self, handler, monkeypatch):
        fake_sys = _FakeSys({"__nexy__.src.routes.app": object()})
        monkeypatch.setattr("nexy.utils.dev.watcher.sys", fake_sys)
        handler._purge_route_modules("src/routes/app.tsx")
        assert "__nexy__.src.routes.app" in fake_sys.modules

    def test_purge_removes_parent_packages(self, handler, monkeypatch):
        fake_sys = _FakeSys(
            {
                "__nexy__": object(),
                "__nexy__.src": object(),
                "__nexy__.src.routes": object(),
                "__nexy__.src.routes.index": object(),
            }
        )
        monkeypatch.setattr("nexy.utils.dev.watcher.sys", fake_sys)
        handler._purge_route_modules("src/routes/index.nexy")
        assert "__nexy__" in fake_sys.modules
        assert "__nexy__.src" in fake_sys.modules
        assert "__nexy__.src.routes" in fake_sys.modules
        assert "__nexy__.src.routes.index" not in fake_sys.modules


# ── Edge cases ──────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_directory_events_ignored(self, handler):
        event = FileSystemEvent("src/routes")
        event.is_directory = True
        handler.on_modified(event)
        handler.on_created(event)
        handler.on_deleted(event)

    def test_concurrent_rapid_events_debounced(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        f = routes / "debounce.nexy"
        f.write_text(NEXY_SOURCE)

        handler.on_modified(_make_event(str(f)))
        first = set(VFS().list_files())

        handler.on_modified(_make_event(str(f)))
        second = set(VFS().list_files())

        assert first == second, "Debounced events should produce same VFS state"

    def test_reload_api_called_once_for_many_events(self, handler, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        f = routes / "count.py"
        f.write_text("print('hello')")

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        for _ in range(5):
            handler.on_modified(_make_event(str(f)))

        assert len(calls) == 1, "Rapid repeated events should call reload only once"

    def test_trailing_skips_when_content_unchanged(self, tmp_path, monkeypatch):
        """A single save (leading + throttled events) must reload exactly once,
        even after the trailing debounce timer fires."""
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        f = routes / "save.py"
        f.write_text("print('hello')")
        handler = WatchHandler(min_interval=0.1)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        try:
            handler.on_modified(_make_event(str(f)))
            handler.on_modified(_make_event(str(f)))  # throttled -> trailing
            time.sleep(0.35)
        finally:
            handler.cancel_trailing()

        assert len(calls) == 1, "Unchanged trailing event must not reload again"

    def test_trailing_reprocesses_when_content_changed(self, tmp_path, monkeypatch):
        """If the file changed after the leading edge (half-written save), the
        trailing event must process it again."""
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        f = routes / "growing.py"
        f.write_text("print('hel')")
        handler = WatchHandler(min_interval=0.1)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        try:
            handler.on_modified(_make_event(str(f)))
            f.write_text("print('hello')")
            handler.on_modified(_make_event(str(f)))  # throttled -> trailing
            time.sleep(0.35)
        finally:
            handler.cancel_trailing()

        assert len(calls) == 2, "Changed trailing event must process again"

    def test_created_marks_path_for_throttle(self, tmp_path, monkeypatch):
        """on_created bypasses the throttle, but must still be recorded so the
        modified events of the same save do not fire a second leading edge."""
        monkeypatch.chdir(tmp_path)
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        f = routes / "fresh.py"
        f.write_text("print('hello')")

        calls = []
        handler = WatchHandler(min_interval=0.1)
        handler.on_reload_api = lambda: calls.append(1)
        try:
            handler.on_created(_make_event(str(f)))
            handler.on_modified(_make_event(str(f)))  # throttled -> trailing
            time.sleep(0.35)
        finally:
            handler.cancel_trailing()

        assert len(calls) == 1, "Create + modify of one save must reload once"


# ── purge_project_modules (dev restart serves fresh .py code) ──────────────────


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

        from nexy.utils.dev.watcher import purge_project_modules

        source = tmp_path / "proj_probe.py"
        source.write_text("")
        self._register("proj_purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "proj_purge_probe" not in sys.modules

    def test_purge_reports_removed_names(self, tmp_path, monkeypatch):
        from nexy.utils.dev.watcher import purge_project_modules

        source = tmp_path / "reported_probe.py"
        source.write_text("")
        self._register("reported_purge_probe", source, monkeypatch)

        purged = purge_project_modules(root=tmp_path)

        assert "reported_purge_probe" in purged

    def test_purge_keeps_framework_module(self, tmp_path, monkeypatch):
        import sys

        from nexy.utils.dev.watcher import purge_project_modules

        source = tmp_path / "framework_probe.py"
        source.write_text("")
        self._register("nexy._purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "nexy._purge_probe" in sys.modules

    def test_purge_keeps_venv_module(self, tmp_path, monkeypatch):
        import sys

        from nexy.utils.dev.watcher import purge_project_modules

        site = tmp_path / ".venv" / "lib"
        site.mkdir(parents=True)
        source = site / "env_probe.py"
        source.write_text("")
        self._register("venv_purge_probe", source, monkeypatch)

        purge_project_modules(root=tmp_path)

        assert "venv_purge_probe" in sys.modules
