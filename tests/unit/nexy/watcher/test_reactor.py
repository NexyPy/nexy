"""What the dev server does for each kind of change."""

from __future__ import annotations

from pathlib import Path

import pytest

from nexy.helpers.fs.vfs import VFS
from nexy.modules.cli.devtools.watch import notify
from nexy.modules.cli.devtools.watch.changes import FileChange
from nexy.modules.cli.devtools.watch.reactor import ChangeReactor
from nexy.modules.compiler import Compiler
from nexy.modules.runtime.hmr import HMR_MANAGER

PAGES = ["about.nexy", "guide.md", "post.mdx", "users.tsx"]


class Calls:
    def __init__(self) -> None:
        self.restarts = 0
        self.structure: list[str] = []
        self.compiled: list[str] = []
        self.broadcasts: list[str] = []

    def restart(self) -> None:
        self.restarts += 1

    def changed(self, path: str) -> None:
        self.structure.append(path)


class FakeCompiler:
    def __init__(self, calls: Calls, fail: Exception | None = None) -> None:
        self.calls = calls
        self.fail = fail

    def compile(self, path: str) -> None:
        if self.fail:
            raise self.fail
        self.calls.compiled.append(path)


@pytest.fixture(autouse=True)
def _clean_vfs():
    yield
    VFS().clear()


@pytest.fixture
def calls() -> Calls:
    return Calls()


@pytest.fixture
def project(nexy_project, tmp_path: Path, monkeypatch) -> Path:
    nexy_project("useFF = react()", imports="from nexy.frontend import react\n")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "routes").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def reactor(calls: Calls, project: Path) -> ChangeReactor:
    del project  # the project must exist (cwd and config) before the reactor reads them
    return ChangeReactor(FakeCompiler(calls), calls.restart, calls.changed)


@pytest.fixture(autouse=True)
def _hmr(calls: Calls, monkeypatch):
    async def broadcast(path: str = "") -> None:
        calls.broadcasts.append(path)

    monkeypatch.setattr(HMR_MANAGER, "loop", object())
    monkeypatch.setattr(HMR_MANAGER, "broadcast_reload", broadcast)
    monkeypatch.setattr(notify, "_run_on_hmr_loop", lambda coroutine: _drive(coroutine))


def _drive(coroutine) -> None:
    import asyncio

    asyncio.run(coroutine)


def _file(root: Path, rel: str, text: str = "x") -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


class TestPagesThatAppear:
    @pytest.mark.parametrize("name", PAGES)
    def test_a_new_page_changes_the_routes(self, reactor, calls, project, name):
        rel = _file(project, f"src/routes/{name}")
        reactor.react(FileChange("created", rel))
        assert calls.structure == [rel]

    def test_a_new_python_route_restarts_the_server(self, reactor, calls, project):
        rel = _file(project, "src/routes/users.py", "x = 1\n")
        reactor.react(FileChange("created", rel))
        assert calls.restarts == 1 and calls.structure == []

    def test_a_new_file_outside_the_routes_is_left_to_vite(self, reactor, calls, project):
        rel = _file(project, "src/components/card.tsx")
        reactor.react(FileChange("created", rel))
        assert calls.structure == [] and calls.restarts == 0


class TestPagesThatDisappear:
    @pytest.mark.parametrize("name", PAGES)
    def test_a_removed_page_changes_the_routes(self, reactor, calls, name):
        reactor.react(FileChange("deleted", f"src/routes/{name}"))
        assert calls.structure == [f"src/routes/{name}"]

    def test_a_removed_python_route_restarts_the_server(self, reactor, calls):
        reactor.react(FileChange("deleted", "src/routes/users.py"))
        assert calls.restarts == 1

    def test_a_removed_file_outside_the_routes_is_ignored(self, reactor, calls):
        reactor.react(FileChange("deleted", "src/components/card.tsx"))
        assert calls.structure == [] and calls.restarts == 0

    def test_a_removed_component_refreshes_the_browser(self, reactor, calls):
        reactor.react(FileChange("deleted", "src/components/card.nexy"))
        assert calls.broadcasts == ["src/components/card.nexy"]


class TestDirectories:
    def test_a_new_directory_of_pages_changes_the_routes(self, reactor, calls):
        reactor.react(FileChange("created", "src/routes/blog"))
        assert calls.structure == ["src/routes/blog"]

    def test_a_removed_directory_of_pages_changes_the_routes(self, reactor, calls):
        reactor.react(FileChange("deleted", "src/routes/blog"))
        assert calls.structure == ["src/routes/blog"]

    def test_a_touched_directory_changes_nothing(self, reactor, calls):
        reactor.react(FileChange("modified", "src/routes/blog"))
        assert calls.structure == []

    def test_a_directory_outside_the_routes_is_ignored(self, reactor, calls):
        reactor.react(FileChange("deleted", "src/components/ui"))
        assert calls.structure == []


class TestEditedFiles:
    def test_a_page_is_compiled_then_the_browser_refreshes(self, reactor, calls, project):
        rel = _file(project, "src/routes/about.nexy")
        reactor.react(FileChange("modified", rel))
        assert calls.compiled == [rel] and calls.broadcasts == [rel]

    def test_a_page_edit_does_not_change_the_routes(self, reactor, calls, project):
        rel = _file(project, "src/routes/about.nexy")
        reactor.react(FileChange("modified", rel))
        assert calls.structure == [] and calls.restarts == 0

    def test_a_markdown_page_refreshes_the_browser(self, reactor, calls, project):
        rel = _file(project, "src/routes/guide.md")
        reactor.react(FileChange("modified", rel))
        assert calls.broadcasts == [rel]

    def test_an_mdx_page_is_compiled_but_left_to_vite(self, reactor, calls, project):
        rel = _file(project, "src/routes/post.mdx")
        reactor.react(FileChange("modified", rel))
        assert calls.compiled == [rel] and calls.broadcasts == []

    def test_a_framework_file_is_left_to_vite(self, reactor, calls, project):
        rel = _file(project, "src/components/card.tsx")
        reactor.react(FileChange("modified", rel))
        assert calls.compiled == [] and calls.broadcasts == [] and calls.restarts == 0

    def test_python_restarts_the_server_without_a_broadcast(self, reactor, calls, project):
        rel = _file(project, "src/services.py", "x = 1\n")
        reactor.react(FileChange("modified", rel))
        assert calls.restarts == 1 and calls.broadcasts == []

    def test_a_file_that_vanished_is_skipped(self, reactor, calls):
        reactor.react(FileChange("modified", "src/gone.py"))
        assert calls.restarts == 0


class TestBrokenFiles:
    def test_python_that_does_not_parse_keeps_the_running_server(self, reactor, calls, project):
        rel = _file(project, "src/routes/users.py", "def GET(:\n")
        reactor.react(FileChange("modified", rel))
        assert calls.restarts == 0

    def test_python_that_does_not_parse_says_what_is_wrong(self, reactor, project, capsys):
        rel = _file(project, "src/routes/users.py", "def GET(:\n")
        reactor.react(FileChange("modified", rel))
        assert "SyntaxError" in capsys.readouterr().out

    def test_a_page_that_does_not_compile_is_reported_and_not_refreshed(
        self, calls, project, capsys
    ):
        reactor = ChangeReactor(FakeCompiler(calls, RuntimeError("bad page")), calls.restart)
        rel = _file(project, "src/routes/about.nexy")
        reactor.react(FileChange("modified", rel))
        assert "bad page" in capsys.readouterr().out and calls.broadcasts == []

    def test_a_reload_that_fails_is_reported_not_raised(self, project, capsys):
        def failing() -> None:
            raise OSError("port busy")

        reactor = ChangeReactor(Compiler(), failing)
        rel = _file(project, "src/services.py", "x = 1\n")
        reactor.react(FileChange("modified", rel))
        assert "port busy" in capsys.readouterr().out


class TestBatches:
    def test_many_python_files_restart_the_server_once(self, reactor, calls, project):
        changes = [
            FileChange("modified", _file(project, f"src/m{n}.py", "x = 1\n")) for n in range(3)
        ]
        reactor.react_all(changes)
        assert calls.restarts == 1

    def test_the_next_batch_can_restart_again(self, reactor, calls, project):
        change = FileChange("modified", _file(project, "src/m.py", "x = 1\n"))
        reactor.react_all([change])
        reactor.react_all([change])
        assert calls.restarts == 2

    def test_a_deleted_folder_of_python_routes_restarts_once(self, reactor, calls):
        reactor.react_all(
            [
                FileChange("deleted", "src/routes/blog"),
                FileChange("deleted", "src/routes/blog/__init__.py"),
                FileChange("deleted", "src/routes/blog/index.py"),
            ]
        )
        assert calls.restarts == 1 and calls.structure == ["src/routes/blog"]


class TestTiming:
    def test_the_timing_is_logged_when_debugging(self, monkeypatch, capsys):
        monkeypatch.setenv("NEXY_HMR_DEBUG", "1")
        notify._log_hmr_timing("src/routes/index.nexy", 0.0)
        assert "hmr" in capsys.readouterr().out

    def test_it_is_silent_otherwise(self, monkeypatch, capsys):
        monkeypatch.delenv("NEXY_HMR_DEBUG", raising=False)
        notify._log_hmr_timing("src/routes/index.nexy", 0.0)
        assert capsys.readouterr().out == ""

    def test_it_is_silent_without_a_start_time(self, monkeypatch, capsys):
        monkeypatch.setenv("NEXY_HMR_DEBUG", "1")
        notify._log_hmr_timing("src/routes/index.nexy", None)
        assert capsys.readouterr().out == ""


class TestCompiledModules:
    class _FakeSys:
        def __init__(self, modules: dict):
            self.modules = modules

    @pytest.mark.parametrize("path", ["src/routes/index.nexy", "src/routes/index.md"])
    def test_the_compiled_module_of_a_page_is_forgotten(self, path, monkeypatch):
        fake = self._FakeSys({"__nexy__.src.routes.index": object(), "__nexy__.src": object()})
        monkeypatch.setattr(notify, "sys", fake)
        notify.forget_compiled_page(path)
        assert list(fake.modules) == ["__nexy__.src"]

    def test_a_framework_file_keeps_its_module(self, monkeypatch):
        fake = self._FakeSys({"__nexy__.src.routes.app": object()})
        monkeypatch.setattr(notify, "sys", fake)
        notify.forget_compiled_page("src/routes/app.tsx")
        assert "__nexy__.src.routes.app" in fake.modules
