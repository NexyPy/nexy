import os
from pathlib import Path

import pytest

from nexy.helpers.fs.vfs import VFS
from nexy.modules.builder import Builder
from nexy.modules.builder.discovery import Discovery


class TestBuilderDiscovery:
    def test_discovers_route_files(self, builder_project: Path) -> None:
        (builder_project / "about.nexy").write_text("---\n---\n<p>about</p>", encoding="utf-8")
        (builder_project / "__nexy__").mkdir()
        (builder_project / "__nexy__" / "junk.nexy").write_text(
            "---\n---\n<p>x</p>", encoding="utf-8"
        )

        files = Discovery().scan(Path("src"))

        names = [f.name for f in files]
        assert "index.nexy" in names
        assert "about.nexy" in names
        # The VFS directory is a build output, not a route source.
        assert "junk.nexy" not in names


class TestBuilderBuild:
    @pytest.mark.usefixtures("builder_project")
    def test_build_compiles_route_into_vfs(self) -> None:
        result = Builder().build()

        assert result.failed == []
        assert result.errors == {}
        assert result.success == ["src/routes/index.nexy"]

        vfs = VFS()
        html_outputs = [f for f in vfs.list_files() if f.endswith(".html")]
        assert len(html_outputs) == 1
        assert len(vfs.read(html_outputs[0])) > 0

    @pytest.mark.usefixtures("builder_project")
    def test_second_build_serves_from_cache(self) -> None:
        builder = Builder()
        first = builder.build()

        second = builder.build()

        assert first.skipped == []
        assert second.skipped == ["src/routes/index.nexy"]
        assert second.success == []

    def test_changed_route_invalidates_cache(self, builder_project: Path) -> None:
        builder = Builder()
        builder.build()

        route = builder_project / "index.nexy"
        route.write_text("---\n---\n<section><p>CHANGED</p></section>", encoding="utf-8")
        # stat-based fingerprints need a strictly newer mtime than the first build.
        os.utime(route, ns=(os.stat(route).st_mtime_ns + 1_000_000,) * 2)

        rebuilt = builder.build()

        assert rebuilt.skipped == []
        assert rebuilt.success == ["src/routes/index.nexy"]
        html_outputs = [f for f in VFS().list_files() if f.endswith(".html")]
        assert any("CHANGED" in VFS().read(f) for f in html_outputs)

    def test_broken_route_reports_build_error(self, builder_project: Path) -> None:
        (builder_project / "index.nexy").write_text(
            "---\ndef broken(\n---\n<section></section>", encoding="utf-8"
        )

        result = Builder().build(showlog=False)

        assert "src/routes/index.nexy" in result.failed
        error = result.errors["src/routes/index.nexy"]
        assert "'(' was never closed" in error.message
