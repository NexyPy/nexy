import re
from pathlib import Path

import pytest

from nexy.modules.frontend import FrontendGenerator


class TestRouteTreeManifest:
    """routes.auto.ts is the shared contract between server and client."""

    def _routes(self, tmp_path: Path) -> Path:
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        (routes / "index.tsx").write_text("export default function Home() { return null }")
        blog = routes / "blog"
        blog.mkdir()
        (blog / "index.tsx").write_text("export default function Blog() { return null }")
        (blog / "[slug].tsx").write_text(
            "export default function Post({ slug }: { slug: string }) { return null }"
        )
        (blog / "layout.tsx").write_text(
            "export default function Layout({ children }: any) { return children }"
        )
        return routes

    def test_generates_manifest_with_paths(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert 'path: "/"' in manifest
        assert 'path: "/blog"' in manifest
        assert 'path: "/blog/{slug}"' in manifest

    def test_manifest_includes_component_file_ref(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert 'file: "/src/routes/blog/[slug].tsx"' in manifest
        assert 'file: "/src/routes/index.tsx"' in manifest

    def test_manifest_marks_layout_chain(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert 'layout: "/src/routes/blog/layout.tsx"' in manifest

    def test_manifest_marks_dynamic_params(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert 'params: ["slug"]' in manifest

    def test_manifest_excludes_special_files(self, tmp_path, monkeypatch):
        routes = self._routes(tmp_path)
        (routes / "loading.tsx").write_text("export default function Loading() { return null }")
        (routes / "errors.tsx").write_text("export default function Errors() { return null }")
        (routes / "notfound.tsx").write_text("export default function NotFound() { return null }")
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert "loading.tsx" not in manifest
        assert "errors.tsx" not in manifest
        assert "notfound.tsx" not in manifest
        assert 'path: "/"' in manifest

    def test_manifest_emits_typed_route_union(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert "export type Route = " in manifest
        assert '"/"' in manifest
        assert "`/blog/${string}`" in manifest

    def test_manifest_route_union_uses_template_literal_for_params(self, tmp_path, monkeypatch):
        routes = self._routes(tmp_path)
        (routes / "blog" / "[tag].tsx").write_text(
            "export default function Tag({ tag }: { tag: string }) { return null }"
        )
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        assert "`/blog/${string}`" in manifest

    def test_manifest_route_union_deduplicates_paths(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        (tmp_path / "src" / "routes" / "index.nexy").write_text("---\n---\n<div>Home</div>")
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        manifest = gen.generate_route_manifest()
        assert manifest is not None
        route_line = next(
            line for line in manifest.splitlines() if line.startswith("export type Route")
        )
        assert route_line.count('"/"') == 1

    def test_writes_manifest_to_nexy_src(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        gen._write_route_manifest()
        target = tmp_path / "__nexy__" / "src" / "routes.auto.ts"
        assert target.is_file()
        content = target.read_text(encoding="utf-8")
        assert "export const NEXY_ROUTES" in content

    def test_writes_client_manifest_to_nexy_src(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        gen._write_route_manifest()
        target = tmp_path / "__nexy__" / "src" / "routes.client.auto.ts"
        assert target.is_file()
        content = target.read_text(encoding="utf-8")
        assert "export const NEXY_ROUTES" in content
        assert 'path: "/"' in content

    @pytest.mark.parametrize("name", ["routes.auto.ts", "routes.client.auto.ts"])
    def test_a_project_without_routes_still_gets_both_manifests(self, tmp_path, monkeypatch, name):
        # The client runtime imports both files, so a modular project (no src/routes) needs them:
        # Vite stops with "Failed to resolve import" when one is missing.
        monkeypatch.chdir(tmp_path)
        FrontendGenerator()._write_route_manifest()
        assert (tmp_path / "__nexy__" / "src" / name).is_file()

    def test_the_manifest_of_a_project_without_routes_lists_none(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        FrontendGenerator()._write_route_manifest()
        content = (tmp_path / "__nexy__" / "src" / "routes.client.auto.ts").read_text("utf-8")
        assert "export const NEXY_ROUTES: NexyRoute[] = [\n];" in content

    def test_client_manifest_excludes_server_rendered_pages(self, tmp_path, monkeypatch):
        routes = self._routes(tmp_path)
        (routes / "index.nexy").write_text("---\n---\n<div>Home</div>")
        (routes / "about.md").write_text("# About")
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        client = gen.generate_client_route_manifest()
        assert client is not None
        assert ".nexy" not in client
        assert ".md" not in client
        assert ".mdx" not in client
        assert 'file: "/src/routes/index.tsx"' in client


class TestClientRouterGeneration:
    """The generated runtime.ts wires the shared manifest to the client router."""

    def _generate(self, tmp_path, monkeypatch) -> str:
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        gen.generate()
        return (tmp_path / "__nexy__" / "src" / "runtime.ts").read_text(encoding="utf-8")

    def _routes(self, tmp_path: Path) -> Path:
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        (routes / "index.tsx").write_text("export default function Home() { return null }")
        (routes / "index.nexy").write_text("---\n---\n<div>Home</div>")
        return routes

    def test_runtime_imports_shared_manifest(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "import { NEXY_ROUTES" in content

    def test_runtime_imports_client_manifest(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "routes.client.auto.ts" in content

    def test_runtime_glob_excludes_mdx(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "import.meta.glob" in content
        assert "mdx" not in content.split("import.meta.glob")[1].split(")")[0]

    def _router(self, tmp_path) -> str:
        return (tmp_path / "__nexy__" / "src" / "router.ts").read_text(encoding="utf-8")

    def test_runtime_matches_routes_and_drives_the_router(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "matchRoute" in content and "createRouter" in content
        assert "w.__nexy_router = router" in content

    def test_the_router_pushes_history_after_rendering(self, tmp_path, monkeypatch):
        self._generate(tmp_path, monkeypatch)
        router = self._router(tmp_path)
        assert "pushState" in router and "replaceState" in router

    def test_the_router_handles_popstate_without_reloading(self, tmp_path, monkeypatch):
        self._generate(tmp_path, monkeypatch)
        router = self._router(tmp_path)
        assert "popstate" in router
        assert "location.reload" not in router

    def test_the_router_only_starts_for_a_project_with_client_routes(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "if (NEXY_ROUTES.some(isNavigable)) router.start();" in content

    def test_navigation_does_not_fetch_a_full_document(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        router = self._router(tmp_path)
        for source in (content, router):
            assert not re.search(r"\bfetch\(", source) and "DOMParser" not in source

    def test_runtime_catch_all_matches_multiple_segments(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "isCatchAll ? parts.length < segs.length" in content

    def test_keys_auto_only_indexes_navigable_files(self, tmp_path, monkeypatch):
        self._routes(tmp_path)
        (tmp_path / "src" / "routes" / "index.nexy").write_text("---\n---\n<div>Home</div>")
        (tmp_path / "src" / "routes" / "about.md").write_text("# About")
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        gen.generate()
        keys = (tmp_path / "__nexy__" / "src" / "keys.auto.ts").read_text(encoding="utf-8")
        assert "index.tsx" in keys
        assert ".nexy" not in keys
        assert ".md" not in keys
        assert ".mdx" not in keys


class TestClientAdapters:
    """Each project gets the Link, Image and hooks of its own framework, and nothing else."""

    FILES = {
        "react": {"client.ts"},
        "preact": {"client.ts"},
        "vue": {"client.ts"},
        "solid": {"client.tsx"},
        "svelte": {"client.ts", "Link.svelte", "Image.svelte"},
    }
    EVERY_ADAPTER_FILE = {"client.ts", "client.tsx", "Link.svelte", "Image.svelte", "Link.tsx"}

    def _generate(self, tmp_path, nexy_project, framework: str | None) -> Path:
        if framework:
            nexy_project(
                f"useFF = {framework}()", imports=f"from nexy.frontend import {framework}\n"
            )
        else:
            nexy_project("")
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True, exist_ok=True)
        (routes / "index.tsx").write_text("export default function Home() { return null }")
        FrontendGenerator().generate()
        return tmp_path / "__nexy__" / "src"

    @pytest.mark.parametrize("framework", sorted(FILES))
    def test_the_adapter_of_the_framework_is_written(self, tmp_path, nexy_project, framework):
        src = self._generate(tmp_path, nexy_project, framework)
        present = {name for name in self.EVERY_ADAPTER_FILE if (src / name).is_file()}
        assert present == self.FILES[framework]

    @pytest.mark.parametrize("framework", sorted(FILES))
    def test_the_shared_modules_come_with_it(self, tmp_path, nexy_project, framework):
        src = self._generate(tmp_path, nexy_project, framework)
        assert (src / "router.ts").is_file() and (src / "shared.ts").is_file()

    def test_a_project_without_a_framework_gets_no_adapter(self, tmp_path, nexy_project):
        src = self._generate(tmp_path, nexy_project, None)
        assert not any((src / name).exists() for name in self.EVERY_ADAPTER_FILE)

    def test_switching_framework_removes_the_old_adapter(self, tmp_path, nexy_project):
        src = self._generate(tmp_path, nexy_project, "svelte")
        assert (src / "Link.svelte").is_file()
        self._generate(tmp_path, nexy_project, "react")
        assert not (src / "Link.svelte").exists() and (src / "client.ts").is_file()

    def test_the_legacy_react_only_link_is_gone(self, tmp_path, nexy_project):
        src = self._generate(tmp_path, nexy_project, "react")
        assert not (src / "Link.tsx").exists()

    @pytest.mark.parametrize("framework", sorted(FILES))
    def test_links_are_typed_by_the_routes_of_the_project(self, tmp_path, nexy_project, framework):
        src = self._generate(tmp_path, nexy_project, framework)
        adapter = next(src / n for n in ("client.tsx", "client.ts") if (src / n).is_file())
        content = adapter.read_text(encoding="utf-8")
        assert "from './routes.auto.ts'" in content and "export type Href" in content

    @pytest.mark.parametrize("framework", sorted(FILES))
    def test_links_carry_the_router_marker(self, tmp_path, nexy_project, framework):
        src = self._generate(tmp_path, nexy_project, framework)
        names = sorted(self.FILES[framework] - {"Image.svelte"})
        text = "".join((src / n).read_text(encoding="utf-8") for n in names)
        assert "data-nexy-link" in text
