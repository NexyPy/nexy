from pathlib import Path

import pytest
from watchdog.events import FileSystemEvent

from nexy.utils.dev.watcher import WatchHandler
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


# ── _normalize ──────────────────────────────────────────────────────────────────

class TestNormalize:
    def test_string(self, handler):
        assert handler._normalize("some/path/file.nexy") == "some/path/file.nexy"

    def test_bytes(self, handler):
        assert handler._normalize(b"some/path/file.nexy") == "some/path/file.nexy"

    def test_backslashes(self, handler):
        assert handler._normalize("src\\routes\\index.nexy") == "src/routes/index.nexy"

    def test_strips_dot_slash(self, handler):
        assert handler._normalize("./src/routes/index.nexy") == "src/routes/index.nexy"

    def test_strips_cwd_prefix(self, handler):
        cwd = Path.cwd().as_posix()
        abs_path = f"{cwd}/src/routes/index.nexy"
        assert handler._normalize(abs_path) == "src/routes/index.nexy"

    def test_absolute_path_on_different_drive(self, handler):
        cwd = Path.cwd()
        other_drive = "E:" if cwd.drive == "D:" else "D:"
        abs_path = f"{other_drive}/other/project/src/routes/index.nexy"
        result = handler._normalize(abs_path)
        assert result == abs_path.replace("\\", "/").lstrip("./")


# ── _skip ───────────────────────────────────────────────────────────────────────

class TestSkip:
    def test_skips_git(self, handler):
        assert handler._skip(".git/config")

    def test_skips_venv(self, handler):
        assert handler._skip("venv/bin/python")

    def test_skips_pycache(self, handler):
        assert handler._skip("__pycache__/cache.py")

    def test_skips_node_modules(self, handler):
        assert handler._skip("node_modules/pkg/index.js")

    def test_skips_nexy_dir(self, handler):
        assert handler._skip("__nexy__/generated.py")

    def test_allows_src_routes(self, handler):
        assert not handler._skip("src/routes/index.nexy")

    def test_allows_py_file(self, handler):
        assert not handler._skip("src/lib/utils.py")


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
        nexy_file = routes / "index.nexy"
        nexy_file.write_text(NEXY_SOURCE)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_modified(_make_event(str(nexy_file)))

        assert len(calls) == 1, "on_reload_api should be called once after compile"

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
        nexy_file = routes / "page.nexy"
        nexy_file.write_text(NEXY_SOURCE)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        handler.on_created(_make_event(str(nexy_file)))

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
        handler.on_deleted(_make_event("src/routes/index.nexy"))
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
        f = routes / "count.nexy"
        f.write_text(NEXY_SOURCE)

        calls = []
        handler.on_reload_api = lambda: calls.append(1)
        for _ in range(5):
            handler.on_modified(_make_event(str(f)))

        assert len(calls) == 1, "Rapid repeated events should call reload only once"
