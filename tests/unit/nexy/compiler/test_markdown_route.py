import ast
import importlib
import json
from pathlib import Path

import pytest

from nexy.compiler.markdown_route import MarkdownRouteCompiler
from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.runtime.importer import install_vfs_importer

MD = "# Hello World\n\nSome **content**.\n"


def _compile(tmp_path: Path, rel_file: str, content: str, *, clear: bool = True) -> None:
    src = tmp_path / rel_file
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(content, encoding="utf-8")
    if clear:
        VFS().clear()
    MarkdownRouteCompiler().compile(input=rel_file)


def _layout_name(tmp_path: Path) -> str:
    name = Config().LAYOUT_FILE_NAMES[0]
    (tmp_path / "src" / "routes" / "app").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "routes" / "app" / name).write_text("---\n---\n<div>{{ children }}</div>\n")
    return name


def test_generated_wrapper_is_valid_python(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, "src/routes/hello.md", MD)
    body = VFS().read("__nexy__/src/routes/hello.py")
    assert isinstance(ast.parse(body), ast.Module)


@pytest.mark.parametrize(
    "stem,py_path,expected_def",
    [
        ("index", "__nexy__/src/routes/index.py", "def Index("),
        ("[slug]", "__nexy__/src/routes/slug_catch_all.py", "def Slug_catch_all("),
    ],
)
def test_wrapper_func_name_matches_component_convention(
    tmp_path, monkeypatch, stem, py_path, expected_def
) -> None:
    monkeypatch.chdir(tmp_path)
    rel_file = f"src/routes/{stem}.md"
    _compile(tmp_path, rel_file, MD)
    body = VFS().read(py_path)
    assert expected_def in body


def test_meta_records_markdown_kind(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, "src/routes/meta.md", MD)
    meta = json.loads(VFS().read("__nexy__/src/routes/meta.meta.json"))
    assert meta["kind"] == "markdown"


def test_unsupported_extension_raises(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "src" / "routes" / "page.txt"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("plain\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported extension"):
        MarkdownRouteCompiler().compile(input="src/routes/page.txt")


def test_layout_import_line_in_generated_source(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _layout_name(tmp_path)
    _compile(tmp_path, "src/routes/app/page.md", MD)
    body = VFS().read("__nexy__/src/routes/app/page.py")
    assert "    from __nexy__.src.routes.app.layout import Layout as __Layout" in body


def test_locale_suffix_sets_meta_and_strips_stem(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "useLocales", ["fr", "en"])
    _compile(tmp_path, "src/routes/docs/about.fr.md", MD)
    meta = json.loads(VFS().read("__nexy__/src/routes/docs/about_fr.meta.json"))
    assert meta["locale"] == "fr" and meta["component_name"] == "About"


def test_wrapper_renders_markdown_with_heading_ids(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/render.md", MD)
    module = importlib.import_module("__nexy__.src.routes.render")
    html = module.Render()
    assert '<h1 id="hello-world">Hello World</h1>' in html


def test_wrapper_publishes_toc_for_use_toc(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/tocpage.md", MD)
    module = importlib.import_module("__nexy__.src.routes.tocpage")
    module.Tocpage()
    from nexy.hooks import _toc_storage

    assert "<h1" in _toc_storage.get()


def test_module_output_is_byte_deterministic(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rel_file = "src/routes/deterministic.md"
    py_path = "__nexy__/src/routes/deterministic.py"
    meta_path = "__nexy__/src/routes/deterministic.meta.json"

    _compile(tmp_path, rel_file, MD)
    first = (VFS().read(py_path), VFS().read(meta_path))
    _compile(tmp_path, rel_file, MD)
    second = (VFS().read(py_path), VFS().read(meta_path))
    assert first == second
