"""Generated TypeScript must not fail the strict typecheck of a user project."""

from __future__ import annotations

from pathlib import Path

from nexy.modules.frontend import FrontendGenerator

HEADER = "// @ts-nocheck\n"


def _generate(tmp_path: Path, nexy_project) -> Path:
    nexy_project("useFF = react()", imports="from nexy.frontend import react\n")
    FrontendGenerator().generate()
    return tmp_path / "__nexy__"


def test_every_generated_typescript_file_is_exempt(tmp_path, nexy_project):
    generated = _generate(tmp_path, nexy_project)
    files = [p for p in generated.rglob("*") if p.suffix in {".ts", ".tsx"}]
    assert files and all(p.read_text(encoding="utf-8").startswith(HEADER) for p in files)


def test_regenerating_does_not_stack_the_header(tmp_path, nexy_project):
    generated = _generate(tmp_path, nexy_project)
    FrontendGenerator().generate()
    content = (generated / "src" / "runtime.ts").read_text(encoding="utf-8")
    assert content.count(HEADER) == 1


def test_project_sources_are_still_typechecked(tmp_path, nexy_project):
    nexy_project("useFF = react()", imports="from nexy.frontend import react\n")
    route = tmp_path / "src" / "routes" / "index.tsx"
    route.parent.mkdir(parents=True)
    original = "export default function Home() { return null }\n"
    route.write_text(original, encoding="utf-8")
    FrontendGenerator().generate()
    assert route.read_text(encoding="utf-8") == original
