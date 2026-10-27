"""Loading the app creates the `__init__.py` files its routes need, with or without the CLI."""

from __future__ import annotations

from nexy.modules.routers.app import AppServer


def test_app_server_adds_init_to_folders_with_python_files(tmp_path, monkeypatch):
    (tmp_path / "src" / "routes" / "users").mkdir(parents=True)
    (tmp_path / "src" / "routes" / "users" / "list.py").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    AppServer()
    assert (tmp_path / "src" / "routes" / "users" / "__init__.py").exists()


def test_app_server_keeps_an_existing_init(tmp_path, monkeypatch):
    package = tmp_path / "src" / "routes"
    package.mkdir(parents=True)
    (package / "a.nexy").write_text("", encoding="utf-8")
    (package / "__init__.py").write_text("X = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    AppServer()
    assert (package / "__init__.py").read_text(encoding="utf-8") == "X = 1\n"
