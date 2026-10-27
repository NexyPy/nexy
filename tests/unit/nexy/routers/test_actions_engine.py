import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI

from nexy.modules.routers.actions.engine import ActionEngine
from nexy.modules.routers.actions.store import ACTIONS_STORE


@pytest.fixture(autouse=True)
def _isolated_store() -> Any:
    registry = dict(ACTIONS_STORE.registry)
    path_map = dict(ACTIONS_STORE.path_map)
    ACTIONS_STORE.registry.clear()
    ACTIONS_STORE.path_map.clear()
    path_snapshot = list(sys.path)
    _drop_src_modules()
    yield
    ACTIONS_STORE.registry.clear()
    ACTIONS_STORE.registry.update(registry)
    ACTIONS_STORE.path_map.clear()
    ACTIONS_STORE.path_map.update(path_map)
    sys.path[:] = path_snapshot
    _drop_src_modules()


def _drop_src_modules() -> None:
    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


def _handler(amount: int, label: str, request: Any = None) -> str:  # noqa: ARG001
    return f"{amount}{label}"


def test_include_router_mounts_post_route() -> None:
    func_id = ACTIONS_STORE.register(_handler)
    router = ActionEngine().include_router(FastAPI())
    route = next(r for r in router.routes if r.path.startswith("/_nx_"))
    assert route.path == f"/_nx_{ACTIONS_STORE._generate_hash(func_id)}"
    assert route.methods == {"POST"}


def test_generate_client_writes_one_typed_module(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    path = ActionEngine(output_dir=str(tmp_path)).generate_client()
    assert path == tmp_path / "actions.ts"


def test_generated_client_types_the_input_and_the_result(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    ActionEngine(output_dir=str(tmp_path)).generate_client()
    generated = (tmp_path / "actions.ts").read_text(encoding="utf-8")
    assert "defineAction<{ amount: number; label: string }, string>" in generated


def test_generated_client_leaves_out_the_injected_arguments(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    ActionEngine(output_dir=str(tmp_path)).generate_client()
    assert "request" not in (tmp_path / "actions.ts").read_text(encoding="utf-8")


def test_generated_client_points_at_the_mounted_path(tmp_path: Path) -> None:
    func_id = ACTIONS_STORE.register(_handler)
    ActionEngine(output_dir=str(tmp_path)).generate_client()
    generated = (tmp_path / "actions.ts").read_text(encoding="utf-8")
    assert f"/_nx_{ACTIONS_STORE._generate_hash(func_id)}" in generated


def test_generated_client_ships_its_runtime(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    ActionEngine(output_dir=str(tmp_path)).generate_client()
    assert "export function defineAction" in (tmp_path / "action-runtime.ts").read_text("utf-8")


def test_an_action_without_input_takes_void(tmp_path: Path) -> None:
    def ping() -> str:
        return "pong"

    ACTIONS_STORE.register(ping)
    ActionEngine(output_dir=str(tmp_path)).generate_client()
    assert "defineAction<void, string>" in (tmp_path / "actions.ts").read_text(encoding="utf-8")


def test_without_actions_a_stale_client_is_removed(tmp_path: Path) -> None:
    (tmp_path / "actions.ts").write_text("old", encoding="utf-8")
    assert ActionEngine(output_dir=str(tmp_path)).generate_client() is None
    assert not (tmp_path / "actions.ts").exists()


def test_discover_skips_missing_directory(tmp_path: Path) -> None:
    ActionEngine().discover(str(tmp_path / "missing"))


def test_discover_says_which_module_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "broken_report.py").write_text(
        "import missing_package_xyz" + chr(10), encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    ActionEngine().discover("src")
    assert "src.broken_report" in capsys.readouterr().out


def test_discover_imports_modules_and_skips_broken(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "ok_mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "broken_mod.py").write_text("import missing_package_xyz\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    ActionEngine().discover("src")
    assert "src.ok_mod" in sys.modules
    assert "src.broken_mod" not in sys.modules


def test_discover_skips_ignored_folders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "src"
    (source / "node_modules").mkdir(parents=True)
    (source / "node_modules" / "__init__.py").write_text("", encoding="utf-8")
    (source / "node_modules" / "bomb.py").write_text(
        "raise RuntimeError('imported')\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    ActionEngine().discover("src")
    assert "src.node_modules.bomb" not in sys.modules


class TestTemplateContext:
    """What a rendered component can call: its actions by name and the paths behind them."""

    @staticmethod
    def _store():
        from nexy.modules.routers.actions.store import ActionsStore

        store = ActionsStore()

        async def create_user() -> None: ...

        create_user.__module__ = "src.actions.user"
        func_id = store.register(create_user)
        return store, func_id, create_user

    def test_each_action_is_available_by_its_function_name(self):
        store, _, handler = self._store()
        assert store.template_context()["create_user"] is handler

    def test_the_actions_map_lists_them(self):
        store, _, handler = self._store()
        assert store.template_context()["__actions"] == {"create_user": handler}

    def test_the_path_map_gives_the_generated_path(self):
        store, func_id, _ = self._store()
        store.path_map[func_id] = "/_nx_abc"
        assert store.template_context()["__actions_path"] == {"create_user": "/_nx_abc"}

    def test_an_action_without_a_path_yet_has_an_empty_one(self):
        store, _, _ = self._store()
        assert store.template_context()["__actions_path"] == {"create_user": ""}

    def test_an_empty_store_has_empty_maps(self):
        from nexy.modules.routers.actions.store import ActionsStore

        assert ActionsStore().template_context() == {"__actions": {}, "__actions_path": {}}
