"""Route pathname derivation for catch-all and dotted route filenames.

The route pathname must strip only the file extension, never truncate at the
first ``.`` inside a dynamic segment such as ``[...path]``.
"""

import importlib
import types

from nexy.core.string import StringTransform
from nexy.modules.routers.fbrouter import FBRouter


def _router(tmp_path, monkeypatch, files: list[str]) -> FBRouter:
    from nexy.core.config import Config
    from nexy.modules.routers.fbrouter.discovery import RouteDiscovery

    routes = tmp_path / "src" / "routes"
    routes.mkdir(parents=True)
    for rel in files:
        target = routes / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "ROUTER_PATH", "src/routes")

    fake = types.ModuleType("fake")

    def _component() -> str:
        return ""

    for comp in ("Path_catch_all", "Slug", "Index", "Guide", "Status"):
        setattr(fake, comp, _component)

    def _fake_import(_name: str, *_args: object, **_kwargs: object):
        return fake

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    router = FBRouter.__new__(FBRouter)
    router.discovery = RouteDiscovery()
    router.string_transform = StringTransform()
    router.error_handlers = []
    router.notfound_handlers = []
    router.loading_handlers = []
    router.modules_meta = []
    router._locale_variants = {}
    router._scan_modules()
    return router


def test_catch_all_pathname_keeps_dynamic_segment(tmp_path, monkeypatch):
    router = _router(tmp_path, monkeypatch, ["docs/[...path].tsx"])
    assert [m["pathname"] for m in router.modules_meta] == ["/docs/{path:path}"]


def test_dynamic_slug_pathname(tmp_path, monkeypatch):
    router = _router(tmp_path, monkeypatch, ["blog/[slug].tsx"])
    assert [m["pathname"] for m in router.modules_meta] == ["/blog/{slug}"]


def test_index_pathname_is_root(tmp_path, monkeypatch):
    router = _router(tmp_path, monkeypatch, ["index.tsx"])
    assert [m["pathname"] for m in router.modules_meta] == ["/"]


def test_nested_literal_pathname(tmp_path, monkeypatch):
    router = _router(tmp_path, monkeypatch, ["docs/guide.tsx"])
    assert [m["pathname"] for m in router.modules_meta] == ["/docs/guide"]


def test_api_py_pathname(tmp_path, monkeypatch):
    router = _router(tmp_path, monkeypatch, ["status.py"])
    assert [m["pathname"] for m in router.modules_meta] == ["/status"]
