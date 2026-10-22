from pathlib import Path

from nexy.frontend import FrontendGenerator


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

    def test_runtime_has_match_route(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "matchRoute" in content
        assert "window.history.pushState" in content

    def test_runtime_handles_popstate_without_reload(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "popstate" in content
        assert "window.location.reload" in content

    def test_runtime_does_not_fetch_full_document(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch)
        assert "fetch(" not in content
        assert "DOMParser" not in content

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


class TestClientLinkComponent:
    """The generated Link.tsx is a typed, Next.js-style client link."""

    def _generate(self, tmp_path, monkeypatch) -> Path:
        self._routes(tmp_path)
        monkeypatch.chdir(tmp_path)
        gen = FrontendGenerator()
        gen.generate()
        return tmp_path / "__nexy__" / "src" / "Link.tsx"

    def _routes(self, tmp_path: Path) -> Path:
        routes = tmp_path / "src" / "routes"
        routes.mkdir(parents=True)
        (routes / "index.tsx").write_text("export default function Home() { return null }")
        return routes

    def test_generates_link_component(self, tmp_path, monkeypatch):
        target = self._generate(tmp_path, monkeypatch)
        assert target.is_file()

    def test_link_is_named_export(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch).read_text(encoding="utf-8")
        assert "export function Link" in content

    def test_link_href_is_typed_route(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch).read_text(encoding="utf-8")
        assert "href: Route" in content
        assert "from '@nexy/routes.auto.ts'" in content

    def test_link_has_no_to_prop(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch).read_text(encoding="utf-8")
        assert "to:" not in content

    def test_link_emits_data_nexy_link(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch).read_text(encoding="utf-8")
        assert "data-nexy-link" in content

    def test_link_prefetches_on_hover(self, tmp_path, monkeypatch):
        content = self._generate(tmp_path, monkeypatch).read_text(encoding="utf-8")
        assert "__nexy_prefetch" in content
