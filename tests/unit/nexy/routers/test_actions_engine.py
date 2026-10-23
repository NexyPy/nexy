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


@pytest.mark.parametrize(
    ("py_type", "expected"),
    [
        (int, "number"),
        (float, "number"),
        (str, "string"),
        (bool, "boolean"),
        (list, "any[]"),
        (list[int], "any[]"),
        (dict, "{ [key: string]: any }"),
        (dict[str, int], "{ [key: string]: any }"),
        (object, "any"),
    ],
)
def test_map_py_type_to_ts(py_type: Any, expected: str) -> None:
    assert ActionEngine()._map_py_type_to_ts(py_type) == expected


def test_include_router_mounts_post_route() -> None:
    func_id = ACTIONS_STORE.register(_handler)
    router = ActionEngine().include_router(FastAPI())
    route = next(r for r in router.routes if r.path.startswith("/_nx_"))
    assert route.path == f"/_nx_{ACTIONS_STORE._generate_hash(func_id)}"
    assert route.methods == {"POST"}


def test_generate_client_writes_typed_function(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    engine = ActionEngine(output_dir=str(tmp_path))
    engine.include_router(FastAPI())
    engine.generate_client()
    generated = next(tmp_path.rglob("_handler.ts")).read_text(encoding="utf-8")
    assert "amount: number" in generated
    assert "label: string" in generated
    assert "request" not in generated
    assert "Promise<string>" in generated


def test_generate_client_without_output_dir_writes_nothing(tmp_path: Path) -> None:
    ACTIONS_STORE.register(_handler)
    ActionEngine(output_dir=None).generate_client()
    assert list(tmp_path.iterdir()) == []


def test_discover_skips_missing_directory(tmp_path: Path) -> None:
    ActionEngine().discover(str(tmp_path / "missing"))


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
