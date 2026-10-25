"""A page that appears, disappears or moves changes the routes `nx dev` serves."""

from __future__ import annotations

from pathlib import Path

import pytest
from watchdog.events import (
    DirDeletedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
)

from nexy.modules.cli.devtools import watcher
from nexy.modules.cli.devtools.watcher import WatchHandler

PAGES = [
    ("about.nexy", "react"),
    ("guide.md", "react"),
    ("post.mdx", "react"),
    ("users.tsx", "react"),
    ("team.vue", "vue"),
    ("docs.svelte", "svelte"),
]


class Calls:
    def __init__(self) -> None:
        self.restarts = 0
        self.structure: list[str] = []

    def restart(self) -> None:
        self.restarts += 1

    def changed(self, path: str) -> None:
        self.structure.append(path)


@pytest.fixture
def calls() -> Calls:
    return Calls()


@pytest.fixture
def framework() -> str:
    return "react"


@pytest.fixture
def handler(calls: Calls, framework: str, nexy_project, tmp_path: Path, monkeypatch):
    if framework == "none":
        nexy_project("")
    else:
        nexy_project(f"useFF = {framework}()", imports=f"from nexy.frontend import {framework}\n")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src" / "routes").mkdir(parents=True)
    monkeypatch.setattr(watcher.Compiler, "compile", lambda *_a, **_k: None)
    return WatchHandler(
        on_reload_api=calls.restart,
        on_routes_changed=calls.changed,
        patterns=["*.py", "*.nexy", "*.md", "*.mdx", "*.tsx", "*.vue", "*.svelte"],
        min_interval=0.0,
    )


def _touch(root: Path, rel: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return str(path)


class TestPagesThatAppear:
    @pytest.mark.parametrize(("name", "framework"), PAGES)
    def test_a_new_page_changes_the_routes(self, handler, calls, tmp_path, name):
        handler.on_created(FileCreatedEvent(_touch(tmp_path, f"src/routes/{name}")))
        assert calls.structure == [f"src/routes/{name}"]

    def test_a_new_python_route_restarts_the_server(self, handler, calls, tmp_path):
        handler.on_created(FileCreatedEvent(_touch(tmp_path, "src/routes/users.py")))
        assert calls.restarts == 1 and calls.structure == []

    def test_a_new_file_outside_the_routes_is_left_to_vite(self, handler, calls, tmp_path):
        handler.on_created(FileCreatedEvent(_touch(tmp_path, "src/components/card.tsx")))
        assert calls.structure == [] and calls.restarts == 0

    @pytest.mark.parametrize("framework", ["none"])
    def test_a_framework_file_is_not_a_page_without_that_framework(self, handler, calls, tmp_path):
        handler.on_created(FileCreatedEvent(_touch(tmp_path, "src/routes/users.tsx")))
        assert calls.structure == []


class TestPagesThatDisappear:
    @pytest.mark.parametrize(("name", "framework"), PAGES)
    def test_a_removed_page_changes_the_routes(self, handler, calls, tmp_path, name):
        handler.on_deleted(FileDeletedEvent(str(tmp_path / "src" / "routes" / name)))
        assert calls.structure == [f"src/routes/{name}"]

    def test_a_removed_python_route_restarts_the_server(self, handler, calls, tmp_path):
        handler.on_deleted(FileDeletedEvent(str(tmp_path / "src" / "routes" / "users.py")))
        assert calls.restarts == 1

    def test_a_removed_file_outside_the_routes_is_ignored(self, handler, calls, tmp_path):
        handler.on_deleted(FileDeletedEvent(str(tmp_path / "src" / "components" / "card.tsx")))
        assert calls.structure == [] and calls.restarts == 0


class TestPagesThatMove:
    def test_a_renamed_page_changes_the_routes(self, handler, calls, tmp_path):
        source = str(tmp_path / "src" / "routes" / "a.nexy")
        target = _touch(tmp_path, "src/routes/b.nexy")
        handler.on_moved(FileMovedEvent(source, target))
        assert set(calls.structure) == {"src/routes/a.nexy", "src/routes/b.nexy"}

    def test_a_page_moved_out_of_the_routes_changes_the_routes(self, handler, calls, tmp_path):
        source = str(tmp_path / "src" / "routes" / "a.nexy")
        target = _touch(tmp_path, "archive/a.nexy")
        handler.on_moved(FileMovedEvent(source, target))
        assert calls.structure == ["src/routes/a.nexy"]


class TestDirectories:
    def test_a_removed_directory_of_pages_changes_the_routes(self, handler, calls, tmp_path):
        handler.dispatch(DirDeletedEvent(str(tmp_path / "src" / "routes" / "blog")))
        assert calls.structure == ["src/routes/blog"]

    def test_a_moved_directory_of_pages_changes_the_routes(self, handler, calls, tmp_path):
        source = str(tmp_path / "src" / "routes" / "blog")
        target = str(tmp_path / "src" / "routes" / "news")
        (tmp_path / "src" / "routes" / "news").mkdir()
        handler.dispatch(DirMovedEvent(source, target))
        assert set(calls.structure) == {"src/routes/blog", "src/routes/news"}

    def test_a_directory_outside_the_routes_is_ignored(self, handler, calls, tmp_path):
        handler.dispatch(DirDeletedEvent(str(tmp_path / "src" / "components" / "ui")))
        assert calls.structure == []

    def test_generated_and_environment_directories_are_ignored(self, handler, calls, tmp_path):
        handler.dispatch(DirDeletedEvent(str(tmp_path / "__nexy__" / "src" / "routes")))
        handler.dispatch(DirDeletedEvent(str(tmp_path / "node_modules" / "x" / "routes")))
        assert calls.structure == []


class TestPagesThatChange:
    def test_an_edited_page_is_recompiled_without_changing_the_routes(
        self, handler, calls, tmp_path
    ):
        handler.on_modified(FileModifiedEvent(_touch(tmp_path, "src/routes/about.nexy")))
        assert calls.structure == [] and calls.restarts == 0

    def test_an_edited_python_file_restarts_the_server(self, handler, calls, tmp_path):
        handler.on_modified(FileModifiedEvent(_touch(tmp_path, "src/services.py")))
        assert calls.restarts == 1
