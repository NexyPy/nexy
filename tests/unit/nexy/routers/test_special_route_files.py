import importlib
import types

from nexy.core.config import Config
from nexy.core.framework_rules import (
    special_names,
)
from nexy.core.models import FrontendFramework
from nexy.modules.frontend.frameworks import react
from nexy.modules.routers.fbrouter.discovery import RouteDiscovery
from nexy.modules.routers.fbrouter.layout import RouteLayout
from nexy.modules.routers.fbrouter.scanner import RouteScanner


class TestSpecialRouteFilesConfig:
    """Special route files (layout/notfound/error) follow the active framework."""

    def test_derive_special_names_default(self):
        names = special_names("layout", {})
        assert names == ["layout.nexy"]

    def test_derive_special_names_with_react(self):
        registry = {"react": react()}
        names = special_names("layout", registry)
        assert "layout.nexy" in names
        assert "layout.tsx" in names

    def test_derive_special_names_with_user_override(self):
        names = special_names("layout", {}, user_exts=[".svelte"])
        assert names == ["layout.nexy", "layout.svelte"]

    def test_derive_notfound_names(self):
        ff = FrontendFramework(name="vue", render="", extension=["vue"])
        names = special_names("notfound", {"vue": ff})
        assert "notfound.vue" in names

    def test_derive_errors_names(self):
        ff = FrontendFramework(name="vue", render="", extension=["vue"])
        names = special_names("errors", {"vue": ff})
        assert "errors.nexy" in names
        assert "errors.vue" in names
        assert "error.nexy" not in names

    def test_derive_loading_names(self):
        ff = FrontendFramework(name="vue", render="", extension=["vue"])
        names = special_names("loading", {"vue": ff})
        assert "loading.nexy" in names
        assert "loading.vue" in names


class TestRouteLayoutFrameworkExtensions:
    """RouteLayout discovers layout.tsx when the active framework is react."""

    def test_find_layout_tsx_at_parent(self, tmp_path, monkeypatch):
        routes = tmp_path / "routes"
        routes.mkdir(parents=True)
        monkeypatch.setattr(Config, "ROUTER_PATH", str(routes))
        monkeypatch.setattr(Config, "LAYOUT_FILE_NAMES", ["layout.nexy", "layout.tsx"])

        blog = routes / "blog"
        blog.mkdir(parents=True)
        (blog / "layout.tsx").write_text("export default function Layout() { return null }")
        posts = blog / "posts"
        posts.mkdir()
        (posts / "page.tsx").write_text("export default function Page() { return null }")

        source_path = str(posts / "page.tsx")
        layout = RouteLayout.get_closest_import(source_path)
        assert layout is not None and "layout" in layout


class TestDiscoveryFrameworkSpecialFiles:
    """RouteDiscovery excludes layout.* special files from route registration."""

    def test_excludes_layout_tsx(self, tmp_path, monkeypatch):
        routes = tmp_path / "routes"
        routes.mkdir(parents=True)
        monkeypatch.setattr(Config, "ROUTER_PATH", str(routes))
        exceptions = ["__init__.py", "layout.nexy", "layout.tsx", "dependencies.py"]
        monkeypatch.setattr(Config, "ROUTE_FILE_EXCEPTIONS", exceptions)

        (routes / "layout.tsx").write_text("export default function Layout() { return null }")
        (routes / "page.tsx").write_text("export default function Page() { return null }")

        discovery = RouteDiscovery()
        files = [f.name for f in discovery.scan()]
        assert "layout.tsx" not in files
        assert "page.tsx" in files


class TestScanCategorizesSpecialFiles:
    """_scan_modules routes errors.*/loading.* into their handler buckets."""

    def test_categorizes_errors_loading_notfound(self, tmp_path, monkeypatch):
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        for name in ("errors.nexy", "loading.nexy", "notfound.nexy", "index.nexy"):
            (routes / name).write_text("")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(Config, "ROUTER_PATH", "src/routes")
        monkeypatch.setattr(Config, "NOTFOUND_FILE_NAMES", ["notfound.nexy"])
        monkeypatch.setattr(Config, "ERROR_FILE_NAMES", ["errors.nexy"])
        monkeypatch.setattr(Config, "LOADING_FILE_NAMES", ["loading.nexy"])
        monkeypatch.setattr(Config, "LAYOUT_FILE_NAMES", ["layout.nexy"])

        fake = types.ModuleType("fake")
        for name in ("Errors", "Loading", "Notfound", "Index"):
            setattr(fake, name, lambda: "")

        def _fake_import(_name: str, *_args: object, **_kwargs: object):
            return fake

        monkeypatch.setattr(importlib, "import_module", _fake_import)

        found = RouteScanner(RouteDiscovery()).scan()

        assert [h.comp for h in found.errors] == ["Errors"]
        assert [h.comp for h in found.notfound] == ["Notfound"]
        assert [h.comp for h in found.loading] == ["Loading"]
        assert [m.pathname for m in found.routes] == ["/"]
