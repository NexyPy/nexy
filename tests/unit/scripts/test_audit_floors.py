"""The audit checks the lowest versions Nexy allows, not only the locked ones (#601)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("audit_floors", ROOT / "scripts" / "audit_floors.py")
assert SPEC is not None and SPEC.loader is not None
audit_floors = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit_floors
SPEC.loader.exec_module(audit_floors)

PYPROJECT = """[project]
dependencies = [
    "starlette>=1.3.1",
    "uvicorn[standard]>=0.40.0",
    "uvloop>=0.21.0; sys_platform != 'win32'",
    "plain",
]
"""
TEMPLATE = '{"dependencies": {"vite": "^6.4.4", "@vitejs/plugin-vue": "^6.0.0", "x": "latest"}}'


def _answer(*vulns: list[str]):
    results = {"results": [{"vulns": [{"id": i} for i in ids]} if ids else {} for ids in vulns]}
    return lambda _body: results


def test_python_floors_are_read_from_the_dependencies(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    floors = audit_floors.python_floors(tmp_path / "pyproject.toml")
    assert floors == {"starlette": "1.3.1", "uvicorn": "0.40.0", "uvloop": "0.21.0"}


def test_npm_floors_are_read_from_the_caret_ranges(tmp_path: Path):
    (tmp_path / "package.json").write_text(TEMPLATE, encoding="utf-8")
    floors = audit_floors.npm_floors(tmp_path / "package.json")
    assert floors == {"vite": "6.4.4", "@vitejs/plugin-vue": "6.0.0"}


def test_a_floor_with_an_advisory_is_reported():
    found = audit_floors.advisories("npm", {"vite": "6.4.3", "vue": "3.5.33"}, _answer(["G1"], []))
    assert found == {"vite": ["G1"]}


def test_an_ignored_advisory_is_not_reported():
    found = audit_floors.advisories(
        "PyPI", {"deep-translator": "1.11.4"}, _answer(["PYSEC-2022-252"])
    )
    assert found == {}


def test_the_audit_fails_when_a_floor_has_an_advisory(monkeypatch):
    monkeypatch.setattr(audit_floors, "_post", _answer(["G1"]))
    assert audit_floors.main() == 1


def test_the_audit_passes_when_no_floor_has_an_advisory(monkeypatch):
    monkeypatch.setattr(audit_floors, "_post", lambda _body: {"results": []})
    assert audit_floors.main() == 0
