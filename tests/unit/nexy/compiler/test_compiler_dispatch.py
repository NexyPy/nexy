import pytest

from nexy.errors import NexyCompileError
from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler import Compiler

DEFAULT_EXPORT = "export default function Page() { return null }\n"


def _write(tmp_path, rel_file: str, content: str) -> None:
    src = tmp_path / rel_file
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(content, encoding="utf-8")


def test_compile_routes_tsx_to_frontend_route_compiler(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path, "src/routes/home.tsx", DEFAULT_EXPORT)
    VFS().clear()
    Compiler().compile(input="src/routes/home.tsx")
    assert VFS().exists("__nexy__/src/routes/home.py")


def test_compile_routes_md_to_markdown_route_compiler(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path, "src/routes/about.md", "# About\n")
    VFS().clear()
    Compiler().compile(input="src/routes/about.md")
    assert VFS().exists("__nexy__/src/routes/about.py")


def test_compile_nexy_still_uses_classic_pipeline(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path, "src/routes/hello.nexy", "---\n---\n<div>Hello</div>\n")
    VFS().clear()
    Compiler().compile(input="src/routes/hello.nexy")
    assert VFS().exists("__nexy__/src/routes/hello.html")


def test_compile_rejects_non_route_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path, "src/routes/data.txt", "plain text\n")
    with pytest.raises(NexyCompileError):
        Compiler().compile(input="src/routes/data.txt")
