import ast
import hashlib
import importlib
import json
from pathlib import Path

import pytest

from nexy.compiler.frontend_route import FrontendRouteCompiler
from nexy.core.config import Config
from nexy.helpers.fs.vfs import VFS
from nexy.runtime.importer import install_vfs_importer

DEFAULT_EXPORT = "export default function Page() { return null }\n"
NAMED_EXPORT = "export function Card() { return null }\n"
NO_EXPORT = "const Item = 1;\n"

# (source, content, expected .py path, expected framework, expected symbol, expected component)
MATRIX = [
    (
        "src/routes/home.tsx",
        DEFAULT_EXPORT,
        "__nexy__/src/routes/home.py",
        "react",
        "default",
        "Home",
    ),
    (
        "src/routes/widgets/card.tsx",
        NAMED_EXPORT,
        "__nexy__/src/routes/widgets/card.py",
        "react",
        "Card",
        "Card",
    ),
    (
        "src/routes/plain.tsx",
        NO_EXPORT,
        "__nexy__/src/routes/plain.py",
        "react",
        "Plain",
        "Plain",
    ),
    (
        "src/routes/about.vue",
        "<template><div /></template>\n",
        "__nexy__/src/routes/about.py",
        "vue",
        "default",
        "About",
    ),
    (
        "src/routes/guide.svelte",
        "<div></div>\n",
        "__nexy__/src/routes/guide.py",
        "svelte",
        "default",
        "Guide",
    ),
    (
        "src/routes/post.mdx",
        "import { useState } from 'preact'\n\n# Post\n",
        "__nexy__/src/routes/post.py",
        "preact",
        "default",
        "Post",
    ),
    (
        "src/routes/docs.mdx",
        "# Docs\n",
        "__nexy__/src/routes/docs.py",
        "react",
        "default",
        "Docs",
    ),
    (
        "src/routes/demo/[slug].tsx",
        DEFAULT_EXPORT,
        "__nexy__/src/routes/demo/slug_catch_all.py",
        "react",
        "default",
        "Slug_catch_all",
    ),
]


def _write_source(tmp_path: Path, rel_file: str, content: str) -> None:
    src = tmp_path / rel_file
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(content, encoding="utf-8")


def _compile(tmp_path: Path, rel_file: str, content: str, *, clear: bool = True) -> str:
    _write_source(tmp_path, rel_file, content)
    if clear:
        VFS().clear()
    FrontendRouteCompiler().compile(input=rel_file)
    return VFS()


def _html_path(py_path: str) -> str:
    return py_path.removesuffix(".py") + ".html"


@pytest.mark.parametrize("case", MATRIX)
def test_generated_wrapper_module_is_valid_python(tmp_path, monkeypatch, case) -> None:
    rel_file, content, py_path, _fw, _symbol, _component = case
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, rel_file, content)
    body = VFS().read(py_path)
    assert isinstance(ast.parse(body), ast.Module)


@pytest.mark.parametrize("case", MATRIX)
def test_ncc_template_declares_framework(tmp_path, monkeypatch, case) -> None:
    rel_file, content, py_path, framework, _symbol, _component = case
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, rel_file, content)
    template = VFS().read(_html_path(py_path))
    assert f'data-nexy-fw="{framework}"' in template


@pytest.mark.parametrize("case", MATRIX)
def test_ncc_template_declares_symbol(tmp_path, monkeypatch, case) -> None:
    rel_file, content, py_path, _fw, symbol, _component = case
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, rel_file, content)
    template = VFS().read(_html_path(py_path))
    assert f'data-nexy-symbol="{symbol}"' in template


@pytest.mark.parametrize("case", MATRIX)
def test_meta_records_component_name(tmp_path, monkeypatch, case) -> None:
    rel_file, content, py_path, _fw, _symbol, component = case
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, rel_file, content)
    meta = json.loads(VFS().read(py_path.removesuffix(".py") + ".meta.json"))
    assert meta["component_name"] == component


@pytest.mark.parametrize(
    "rel_file,content,py_path",
    [
        ("src/routes/home.tsx", DEFAULT_EXPORT, "__nexy__/src/routes/home.py"),
        ("src/routes/post.mdx", "# Post\n", "__nexy__/src/routes/post.py"),
    ],
)
def test_generated_ssg_path_matches_js_writer_convention(
    tmp_path, monkeypatch, rel_file, content, py_path
) -> None:
    """JS SSG (getEntryId) writes default exports as '<name>.Default.html'.

    On Windows a case mismatch would still resolve at runtime, so assert the
    exact bytes of the generated lookup path.
    """
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, rel_file, content)
    body = VFS().read(py_path)
    expected = py_path.removeprefix("__nexy__/").removesuffix(".py") + ".Default.html"
    expected = f"__nexy__/client/static/{expected}"
    assert expected in body


def test_module_output_is_byte_deterministic(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    rel_file = "src/routes/home.tsx"
    content, py_path = DEFAULT_EXPORT, "__nexy__/src/routes/home.py"
    html_path = _html_path(py_path)
    meta_path = py_path.removesuffix(".py") + ".meta.json"

    _compile(tmp_path, rel_file, content)
    first = (VFS().read(py_path), VFS().read(html_path), VFS().read(meta_path))
    _compile(tmp_path, rel_file, content)
    second = (VFS().read(py_path), VFS().read(html_path), VFS().read(meta_path))
    assert first == second


def _mount_id(py_path: str, symbol: str) -> str:
    base = f"{py_path}|{symbol}|1"
    return "nexy-" + hashlib.md5(base.encode("utf-8")).hexdigest()[:10]


def test_wrapper_mount_id_is_stable_md5(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/home.tsx", DEFAULT_EXPORT)
    module = importlib.import_module("__nexy__.src.routes.home")
    html = module.Home()
    expected = _mount_id("__nexy__/src/routes/home.py", "default")
    assert f'id="{expected}"' in html


def test_wrapper_exposes_dev_path_in_dev_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/home.tsx", DEFAULT_EXPORT)
    module = importlib.import_module("__nexy__.src.routes.home")
    assert 'data-nexy-path="/src/routes/home.tsx"' in module.Home()


def test_wrapper_uses_named_export_symbol(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/widgets/card.tsx", NAMED_EXPORT)
    module = importlib.import_module("__nexy__.src.routes.widgets.card")
    assert 'data-nexy-symbol="Card"' in module.Card()


def test_wrapper_uses_default_symbol_for_vue(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/about.vue", "<template><div /></template>\n")
    module = importlib.import_module("__nexy__.src.routes.about")
    assert 'data-nexy-symbol="default"' in module.About()


def test_wrapper_embeds_ssr_html_in_prod_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _compile(tmp_path, "src/routes/prod.tsx", DEFAULT_EXPORT)

    (tmp_path / "__nexy__").mkdir(exist_ok=True)
    (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    ssg_file = tmp_path / "__nexy__" / "client" / "static" / "src" / "routes" / "prod.Default.html"
    ssg_file.parent.mkdir(parents=True, exist_ok=True)
    ssg_file.write_text("<p>SSR-MARKER</p>", encoding="utf-8")

    module = importlib.import_module("__nexy__.src.routes.prod")
    assert "SSR-MARKER" in module.Prod()


def _layout_name(tmp_path: Path) -> str:
    name = Config().LAYOUT_FILE_NAMES[0]
    (tmp_path / "src" / "routes" / "app").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "routes" / "app" / name).write_text("---\n---\n<div>{{ children }}</div>\n")
    return name


def test_layout_import_line_in_generated_source(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _layout_name(tmp_path)
    _compile(tmp_path, "src/routes/app/page.tsx", DEFAULT_EXPORT)
    body = VFS().read("__nexy__/src/routes/app/page.py")
    assert "    from __nexy__.src.routes.app.layout import Layout as __Layout" in body


def test_layout_wrapper_passes_children_to_layout(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    install_vfs_importer()
    _layout_name(tmp_path)
    _compile(tmp_path, "src/routes/app/page.tsx", DEFAULT_EXPORT)
    VFS().write(
        "__nexy__/src/routes/app/layout.py",
        "def Layout(children: str = '', **kwargs) -> str:\n    return 'LAYOUT[' + children + ']'\n",
    )
    module = importlib.import_module("__nexy__.src.routes.app.page")
    page_ncc = f'id="{_mount_id("__nexy__/src/routes/app/page.py", "default")}"'
    html = module.Page()
    assert html.startswith("LAYOUT[<ncc") and page_ncc in html
