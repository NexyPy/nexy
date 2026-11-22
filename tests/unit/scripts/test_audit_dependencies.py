"""The dependency audit checks the version floors once the lock passes (#601)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "audit_dependencies", SCRIPTS / "audit_dependencies.py"
)
assert SPEC is not None and SPEC.loader is not None
audit_dependencies = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_dependencies)


def test_a_lock_that_passes_hands_over_to_the_floor_audit(monkeypatch):
    passed = subprocess.CompletedProcess([], 0, "", "")
    monkeypatch.setattr(audit_dependencies, "_run", lambda _cmd: passed)
    monkeypatch.setattr(audit_dependencies.audit_floors, "main", lambda: 7)
    assert audit_dependencies.main() == 7
