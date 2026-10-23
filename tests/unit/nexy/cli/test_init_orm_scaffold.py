"""Modular ORM scaffolds must keep the controller AppModule expects.

``app_module.py`` unconditionally imports ``AppController`` and ``@Module()``
rejects a class without controllers. The controller used to be rendered only
for ``ORM=None``, so every modular ORM project failed at import time.
"""

from pathlib import Path

from nexy.modules.cli.init.template_setup import _render_local_template

_API_CONFIG = {
    "project_type": "api",
    "FBRouter": False,
    "useCSR": False,
    "client_framework": "none",
    "orm": "SQLModel",
    "db_url": "sqlite:///dev.db",
}


def test_api_modular_orm_scaffold_keeps_app_controller(tmp_path: Path) -> None:
    _render_local_template("api-modular", tmp_path, _API_CONFIG, "demo")
    controller = tmp_path / "src" / "apps" / "app_controller.py"
    assert "class AppController" in controller.read_text(encoding="utf-8")


def test_web_modular_orm_scaffold_keeps_app_controller(tmp_path: Path) -> None:
    config = {**_API_CONFIG, "project_type": "web", "client_framework": "react"}
    _render_local_template("web-modular", tmp_path, config, "demo")
    controller = tmp_path / "src" / "apps" / "app_controller.py"
    assert "class AppController" in controller.read_text(encoding="utf-8")


def test_api_modular_orm_scaffold_wires_users_module(tmp_path: Path) -> None:
    _render_local_template("api-modular", tmp_path, _API_CONFIG, "demo")
    module = (tmp_path / "src" / "apps" / "app_module.py").read_text(encoding="utf-8")
    assert "UsersModule" in module
