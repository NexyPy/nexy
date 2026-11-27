"""Config hooks change only the settings a module declares and keep the rest of the file."""

from __future__ import annotations

import json
from pathlib import Path

from nexy.modules.cli.add.config import apply_config_hooks

CONFIG = (
    "from nexy.core.models import NexyConfigModel\n"
    "\n"
    "\n"
    "class NexyConfig(NexyConfigModel):\n"
    '    useTitle = "Example"\n'
)


def test_apply_config_hooks_replaces_a_python_setting(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("nexyconfig.py").write_text(CONFIG)
    apply_config_hooks({"nexyconfig": {"useTitle": "Changed"}})
    assert 'useTitle = "Changed"' in Path("nexyconfig.py").read_text()


def test_apply_config_hooks_keeps_other_python_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("nexyconfig.py").write_text(CONFIG + "    usePort = 4000\n")
    apply_config_hooks({"nexyconfig": {"useTitle": "Changed"}})
    assert "usePort = 4000" in Path("nexyconfig.py").read_text()


def test_apply_config_hooks_inserts_a_new_python_setting(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("nexyconfig.py").write_text(CONFIG)
    apply_config_hooks({"nexyconfig": {"useSiteUrl": "https://example.com"}})
    assert 'useSiteUrl = "https://example.com"' in Path("nexyconfig.py").read_text()


def test_apply_config_hooks_creates_nexyconfig_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    apply_config_hooks({"nexyconfig": {"useTitle": "Auth"}})
    assert Path("nexyconfig.py").exists()


def test_apply_config_hooks_escapes_a_python_string(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("nexyconfig.py").write_text(CONFIG)
    apply_config_hooks({"nexyconfig": {"useTitle": 'Say "hi"'}})
    assert 'useTitle = "Say \\"hi\\""' in Path("nexyconfig.py").read_text()


def test_apply_config_hooks_writes_a_number(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("nexyconfig.py").write_text(CONFIG)
    apply_config_hooks({"nexyconfig": {"usePort": 4000}})
    assert "usePort = 4000" in Path("nexyconfig.py").read_text()


def test_apply_config_hooks_sets_a_nested_json_value(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("package.json").write_text(json.dumps({"name": "app", "devDependencies": {"vitest": "^2"}}))
    apply_config_hooks({"package_json": {"devDependencies.vitest": "^3"}})
    assert json.loads(Path("package.json").read_text())["devDependencies"]["vitest"] == "^3"


def test_apply_config_hooks_keeps_other_json_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("package.json").write_text(json.dumps({"name": "app"}))
    apply_config_hooks({"package_json": {"scripts.test": "pytest"}})
    assert json.loads(Path("package.json").read_text())["name"] == "app"


def test_apply_config_hooks_creates_package_json_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    apply_config_hooks({"package_json": {"scripts.test": "pytest"}})
    assert json.loads(Path("package.json").read_text()) == {"scripts": {"test": "pytest"}}


def test_apply_config_hooks_reports_each_change(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    changes = apply_config_hooks(
        {"nexyconfig": {"useTitle": "Auth"}, "package_json": {"scripts.test": "pytest"}}
    )
    assert changes == ["nexyconfig.py: useTitle", "package.json: scripts.test"]


def test_apply_config_hooks_reports_nothing_when_there_are_no_hooks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert apply_config_hooks({}) == []
