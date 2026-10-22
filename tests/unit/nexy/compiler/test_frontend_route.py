from pathlib import Path

from nexy.helpers.fs.vfs import VFS
from nexy.modules.compiler.frontend_route import FrontendRouteCompiler
from nexy.modules.runtime.importer import install_vfs_importer


def _compile(tmp_path: Path, rel_file: str) -> None:
    src = tmp_path / rel_file
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("export default function C() { return null }", encoding="utf-8")
    VFS().clear()
    FrontendRouteCompiler().compile(input=rel_file)


def test_generates_init_for_parent_directories(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, "src/routes/demo/[slug].tsx")
    assert VFS().exists("__nexy__/src/routes/demo/__init__.py")


def test_wrapper_func_name_matches_router_convention(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, "src/routes/demo/[slug].tsx")
    body = VFS().read("__nexy__/src/routes/demo/slug_catch_all.py")
    assert "def Slug_catch_all(" in body


def test_wrapper_serializes_path_params_into_ncc_props(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _compile(tmp_path, "src/routes/demo/[slug].tsx")
    import importlib

    install_vfs_importer()
    module = importlib.import_module("__nexy__.src.routes.demo.slug_catch_all")
    html = module.Slug_catch_all(slug="hello")
    assert 'data-nexy-props="{&#34;slug&#34;: &#34;hello&#34;}"' in html
