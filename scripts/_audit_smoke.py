"""Smoke tests for audit - CORRECT API usage based on actual source code."""
from __future__ import annotations

import sys
from pathlib import Path
import tempfile, os

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))

passed = 0
failed = 0


def check(label: str, fn):
    global passed, failed
    try:
        fn()
        print(f"[PASS] {label}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {label}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc(limit=2)
        failed += 1


# ---------- 1. Public API exports ----------
def _test_public_exports():
    import nexy
    for name in ["Audio", "Video", "Form", "Import", "Template", "Vite"]:
        assert hasattr(nexy, name), f"nexy.{name} missing from exports"


check("Public API exports (Audio, Video, Form, Import, Template, Vite)", _test_public_exports)


# ---------- 2. Config singleton ----------
def _test_config():
    from nexy.core.config import Config
    c = Config()
    assert c.ROUTER_PATH == "src/routes", f"unexpected ROUTER_PATH={c.ROUTER_PATH}"
    assert c.PROJECT_ROOT is not None
    assert isinstance(c.ALIASES, dict)
    assert c.useVite is not None
    assert isinstance(c.useFF, list) or c.useFF is None


check("Config singleton loads with all attributes", _test_config)


# ---------- 3. Template rendering with a real temp file ----------
def _test_template():
    from nexy.template import Template, _get_shared_env
    with tempfile.TemporaryDirectory() as td:
        # Write a jinja2 file
        test_j2 = Path(td) / "greeting.nexy"
        test_j2.write_text("<h1>Hello {{ name }}</h1>\n", encoding="utf-8")
        old_cwd = os.getcwd()
        try:
            os.chdir(td)
            t = Template(templates_dir=td)
            out = t.render(str(test_j2.name), {"name": "Nexy"})
            assert "Hello Nexy" in out, f"Expected 'Hello Nexy' in: {out!r}"
        finally:
            os.chdir(old_cwd)
    # Sanity: shared env is one
    env1 = _get_shared_env()
    env2 = _get_shared_env()
    assert env1 is env2, "shared env not singleton"


check("Template.render(file_path, context_dict) works", _test_template)


# ---------- 4. VFS ----------
def _test_vfs():
    from nexy.utils.fs.vfs import VFS
    v = VFS()
    assert v is not None
    assert hasattr(v, "read")
    assert hasattr(v, "exists")
    assert hasattr(v, "index_all")
    assert hasattr(v, "write")


check("VFS has read/exists/index_all/write methods", _test_vfs)


# ---------- 5. i18n core (LocaleManager singleton) ----------
def _test_i18n():
    from nexy.i18n.core import current_locale, _is_rtl
    from contextvars import ContextVar
    assert isinstance(current_locale, ContextVar)
    assert current_locale.get() == "en"
    # RTL check
    assert _is_rtl("ar") is True
    assert _is_rtl("en") is False
    # Call t() which is actually LocaleManager().t via __init__.py
    from nexy.i18n import t as nexy_t
    # Some keys may return default-only
    result = nexy_t("nonexistent_category", "nonexistent_key", default="fallback_ok")
    assert result == "fallback_ok", f"Expected fallback: {result!r}"


check("i18n core: current_locale ContextVar, _is_rtl, t() with default fallback", _test_i18n)


# ---------- 6. Decorators (actual API) ----------
def _test_decorators():
    from nexy.decorators import (
        Container, Module, Controller, UseRoute, UseResponse,
        Action, Injectable, UseGuard, Middleware, UseRoute as _UseRoute
    )
    assert callable(Container)
    assert callable(Module)
    assert callable(Controller)
    assert callable(UseRoute)
    assert callable(UseResponse)
    assert callable(Action)
    assert callable(Injectable)
    assert callable(UseGuard)
    assert callable(Middleware)


check("Decorators real API: Container, Module, Controller, UseRoute, Action, Injectable...", _test_decorators)


# ---------- 7. AppServer/FBRouter ----------
def _test_appserver():
    from nexy.routers.app import AppServer, _server
    from fastapi import FastAPI
    assert isinstance(_server, FastAPI), "_server not a FastAPI"
    assert len(_server.routes) > 0, "no routes registered"
    # At least the favicon/docs/static routes
    route_paths = sorted({r.path for r in _server.routes if hasattr(r, "path")})
    assert "/favicon.ico" in route_paths, f"no favicon route, got: {route_paths}"
    fresh = AppServer().run()
    assert isinstance(fresh, FastAPI)


check("AppServer/FBRouter: routes registered, favicon exists, fresh run() OK", _test_appserver)


# ---------- 8. Builder ----------
def _test_builder():
    from nexy.builder import Builder
    b = Builder()
    assert b is not None
    assert hasattr(b, "compile_single") or hasattr(b, "build"), "no build method on Builder"


check("Builder instantiates and has compile/build method", _test_builder)


# ---------- 9. Frontend framework callables return FrontendFramework ----------
def _test_frontend_registry():
    from nexy.frontend import react, vue, svelte, solid, preact
    from nexy.core.models import FrontendFramework
    for fn in [react, vue, svelte, solid, preact]:
        result = fn()
        assert isinstance(result, FrontendFramework), f"{fn}() returned {type(result)} not FrontendFramework"
        assert isinstance(result.name, str) and len(result.name) > 0
        assert isinstance(result.render, str) and len(result.render) > 0


check("Frontend: react()/vue()/svelte()/solid()/preact() return FrontendFramework(name,render)", _test_frontend_registry)


# ---------- 10. Scanner class ----------
def _test_scanner():
    from nexy.compiler.parser.scanner import Scanner
    from nexy.core.models import ScanResult
    s = Scanner()
    sample = "---\ncount: int = 0\n---\n<div>Hello {{ name }}</div>"
    res: ScanResult = s.scan(sample)
    assert isinstance(res, ScanResult)
    assert "count" in res.logic_block, f"logic missing: {res.logic_block!r}"
    assert "Hello" in res.template_block, f"tpl missing: {res.template_block!r}"
    # No frontmatter
    res2 = s.scan("<p>plain html</p>")
    assert res2.logic_block == ""
    assert "plain html" in res2.template_block


check("Scanner: .scan() splits frontmatter + template correctly", _test_scanner)


# ---------- 11. LogicGenerator class ----------
def _test_generator_logic():
    from nexy.compiler.generator.logic import LogicGenerator
    g = LogicGenerator()
    assert g is not None
    assert hasattr(g, "generate") or hasattr(g, "build"), "LogicGenerator has no generate/build"


check("Compiler Generator: LogicGenerator class instantiates", _test_generator_logic)


# ---------- 12. Errors real API ----------
def _test_errors():
    from nexy.errors import NexyCompileError, NotFound, InternalServerError
    from fastapi import Response
    assert issubclass(NexyCompileError, Exception)
    # NotFound / InternalServerError are callables returning Response
    r1 = NotFound()
    r2 = InternalServerError()
    assert isinstance(r1, Response)
    assert isinstance(r2, Response)


check("Errors real API: NexyCompileError(class), NotFound()/InternalServerError() -> Response", _test_errors)


# ---------- 13. router.py standalone: FileBasedRouter singleton ----------
def _test_standalone_router():
    from nexy.router import FileBasedRouter
    assert FileBasedRouter is not None
    # It's an FBRouter instance
    from nexy.routers.fbrouter import FBRouter
    assert isinstance(FileBasedRouter, FBRouter), f"type={type(FileBasedRouter)}"


check("Router standalone: FileBasedRouter singleton is FBRouter instance", _test_standalone_router)


# ---------- 14. Hooks ----------
def _test_hooks():
    from nexy import hooks
    for name in ["usePathname", "useSearchParams", "useRouter", "useQuery", "useSession", "useCookies", "useToc", "useViews"]:
        assert hasattr(hooks, name), f"hooks.{name} missing"
        assert callable(getattr(hooks, name)), f"hooks.{name} not callable"
    # useLocale from i18n.core
    from nexy.i18n.core import useLocale as _useLocale
    assert callable(_useLocale)


check("Hooks: usePathname/SearchParams/Router/Query/Session/Cookies/Toc/Views + useLocale callable", _test_hooks)


# ---------- 15. Helpers (Form, Image, Link, Audio, Video, Script) ----------
def _test_form_helpers():
    from nexy.form import Form as NexyForm
    from nexy.image import Image as NexyImage
    from nexy.link import Link as NexyLink
    from nexy.audio import Audio as NexyAudio
    from nexy.video import Video as NexyVideo
    from nexy.script import Script
    assert callable(NexyForm)
    assert callable(NexyImage)
    assert callable(NexyLink)
    assert callable(NexyAudio)
    assert callable(NexyVideo)
    assert callable(Script)
    # Image returns a non-empty str
    out = NexyImage(src="/logo.png", alt="Logo")
    assert isinstance(out, str) and "<img" in out.lower(), f"Image(): {out!r:.100}"
    # Link
    out2 = NexyLink(href="/about", children="About")
    assert isinstance(out2, str) and "<a" in out2.lower(), f"Link(): {out2!r:.100}"


check("Helpers: Form/Image/Link/Audio/Video/Script callable, Image+Link return HTML str", _test_form_helpers)


# ---------- 16. Core models ----------
def _test_core_models():
    from nexy.core.models import (
        ScanResult, FrontendFramework, BuildError, LayoutChain,
        RouteDescriptor, RouteMeta, RouteFile, FrameworkFrontend,
    )
    sr = ScanResult(logic_block="x = 1", template_block="<p/>")
    assert sr.logic_block == "x = 1"
    ff = FrontendFramework(name="test", render="console.log(1)")
    assert ff.name == "test"
    be = BuildError(path="/a.nexy", line=5, col=2, type="syntax")
    assert be.path == "/a.nexy"
    assert be.line == 5


check("Core models: ScanResult, FrontendFramework, BuildError dataclasses instantiate correctly", _test_core_models)


# ---------- 17. FBRouter discovery ----------
def _test_fbrouter_discovery():
    from nexy.routers.fbrouter.discovery import RouteDiscovery
    rd = RouteDiscovery()
    assert rd is not None


check("FBRouter: RouteDiscovery class importable", _test_fbrouter_discovery)


# ---------- 18. Actions Engine & Store ----------
def _test_actions():
    from nexy.routers.actions.engine import ACTION_ENGINE
    from nexy.routers.actions.store import ActionsStore, register_action, get_action
    assert ACTION_ENGINE is not None
    store = ActionsStore()
    assert store is not None
    assert callable(register_action)
    assert callable(get_action)


check("Actions system: ACTION_ENGINE, ActionsStore, register_action, get_action", _test_actions)


# ---------- 19. Core types + sandbox ----------
def _test_core_types_sandbox():
    from nexy.core.sandbox import sandboxed_exec
    ns: dict = {}
    sandboxed_exec("x = 1 + 2", ns)
    assert ns.get("x") == 3, f"sandboxed exec failed, ns={ns}"


check("Core sandbox: sandboxed_exec runs isolated code safely", _test_core_types_sandbox)


# ---------- 20. Core string transforms ----------
def _test_core_string():
    from nexy.core.string import StringTransform, Pathname
    assert Pathname.to_snake("HelloWorld") == "hello_world"
    assert Pathname.to_kebab("HelloWorld") == "hello-world"
    assert StringTransform.strip_spaces("  a  b  ") == "a  b"


check("Core string: Pathname snake/kebab, StringTransform.strip_spaces", _test_core_string)


# ---------- SUMMARY ----------
total = passed + failed
print(f"\n====== SMOKE AUDIT: {passed}/{total} passed, {failed} failed ======")
raise SystemExit(0 if failed == 0 else 1)
