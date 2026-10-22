import pytest

from nexy.core.config import Config
from nexy.core.models import FrontendFramework


class TestSingleFrameworkValidation:
    """useFF must configure exactly one frontend framework."""

    def test_single_framework_is_allowed(self):
        ff = FrontendFramework(name="react", render="", extension=["tsx", "jsx"])
        names = Config.derive_special_names("layout", {"react": ff})
        assert "layout.tsx" in names
        assert "layout.jsx" in names

    def test_single_framework_does_not_derive_other_extensions(self):
        ff = FrontendFramework(name="vue", render="", extension=["vue"])
        names = Config.derive_special_names("layout", {"vue": ff})
        assert "layout.vue" in names
        assert "layout.tsx" not in names
        assert "layout.svelte" not in names

    def test_empty_registry_only_keeps_nexy(self):
        names = Config.derive_special_names("layout", {})
        assert names == ["layout.nexy"]


class TestRouteFileExtensionsDerivation:
    """ROUTE_FILE_EXTENSIONS derives from the active framework plus always-on exts."""

    def test_react_active_keeps_nexy_md_mdx_py(self):
        ff = FrontendFramework(name="react", render="", extension=["tsx", "jsx"])
        exts = Config.derive_route_extensions(ff)
        assert ".nexy" in exts
        assert ".md" in exts
        assert ".mdx" in exts
        assert ".py" in exts
        assert ".tsx" in exts
        assert ".jsx" in exts

    def test_react_active_drops_vue_and_svelte(self):
        ff = FrontendFramework(name="react", render="", extension=["tsx", "jsx"])
        exts = Config.derive_route_extensions(ff)
        assert ".vue" not in exts
        assert ".svelte" not in exts

    def test_none_framework_keeps_only_always_on(self):
        exts = Config.derive_route_extensions(None)
        assert exts == [".nexy", ".md", ".mdx", ".py"]


class TestWarnAndSkipOutOfSet:
    """Files outside the active framework set are skipped with a warning."""

    def test_out_of_set_file_is_not_a_route(self, tmp_path, monkeypatch):
        routes = tmp_path / "routes"
        routes.mkdir(parents=True)
        monkeypatch.setattr(Config, "ROUTER_PATH", str(routes))
        ff = FrontendFramework(name="react", render="", extension=["tsx", "jsx"])
        monkeypatch.setattr(Config, "ROUTE_FILE_EXTENSIONS", Config.derive_route_extensions(ff))

        (routes / "page.vue").write_text("<template><div>Vue</div></template>")
        (routes / "page.tsx").write_text("export default function Page() { return null }")

        from nexy.modules.routers.fbrouter.discovery import RouteDiscovery

        discovery = RouteDiscovery()
        files = [f.name for f in discovery.scan()]
        assert "page.tsx" in files
        assert "page.vue" not in files

    def test_two_frameworks_config_is_rejected(self):
        ff1 = FrontendFramework(name="react", render="", extension=["tsx"])
        ff2 = FrontendFramework(name="vue", render="", extension=["vue"])
        with pytest.raises(ValueError, match="exactly one frontend framework"):
            Config.validate_single_framework([ff1, ff2])

    def test_single_framework_passes_validation(self):
        ff = FrontendFramework(name="vue", render="", extension=["vue"])
        assert Config.validate_single_framework(ff) is None
        assert Config.validate_single_framework(None) is None
