"""Every line a change adds to nexy/ runs in a test: the gate reads the diff and the coverage."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "check_diff_coverage.py"


def _load() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("check_diff_coverage", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_diff_coverage"] = module
    spec.loader.exec_module(module)
    return module


gate = _load()

DIFF = """\
diff --git a/nexy/a.py b/nexy/a.py
--- a/nexy/a.py
+++ b/nexy/a.py
@@ -3,0 +4,2 @@ def f():
+    x = 1
+    return x
@@ -10 +12 @@ def g():
+    return 2
diff --git a/docs/page.md b/docs/page.md
--- a/docs/page.md
+++ b/docs/page.md
@@ -1 +1 @@
+text
diff --git a/nexy/gone.py b/nexy/gone.py
--- a/nexy/gone.py
+++ /dev/null
@@ -1 +0,0 @@
"""


def _report(**files: dict) -> dict:
    return {"files": files}


def test_added_lines_are_read_per_file():
    assert gate.added_lines(DIFF) == {"nexy/a.py": {4, 5, 12}}


def test_a_deleted_file_adds_no_line():
    assert "nexy/gone.py" not in gate.added_lines(DIFF)


def test_a_file_outside_the_package_is_not_checked():
    assert "docs/page.md" not in gate.added_lines(DIFF)


def test_a_template_is_not_checked():
    diff = "+++ b/nexy/modules/cli/templates/x.py\n@@ -0,0 +1 @@\n+x\n"
    assert gate.added_lines(diff) == {}


def test_a_covered_change_has_no_gap():
    report = _report(**{"nexy/a.py": {"missing_lines": [7], "missing_branches": []}})
    assert gate.gaps({"nexy/a.py": {4, 5}}, report) == []


def test_an_added_line_no_test_runs_is_a_gap():
    report = _report(**{"nexy/a.py": {"missing_lines": [5], "missing_branches": []}})
    assert gate.gaps({"nexy/a.py": {4, 5}}, report) == ["nexy/a.py:5 never runs in a test"]


def test_an_added_branch_no_test_takes_is_a_gap():
    report = _report(**{"nexy/a.py": {"missing_lines": [], "missing_branches": [[4, 6]]}})
    expected = ["nexy/a.py:4 has a branch no test takes (to line 6)"]
    assert gate.gaps({"nexy/a.py": {4}}, report) == expected


def test_a_branch_that_exits_the_function_says_so():
    report = _report(**{"nexy/a.py": {"missing_lines": [], "missing_branches": [[4, -1]]}})
    expected = ["nexy/a.py:4 has a branch no test takes (to the exit)"]
    assert gate.gaps({"nexy/a.py": {4}}, report) == expected


def test_a_changed_file_no_test_imports_is_a_gap():
    found = gate.gaps({"nexy/new.py": {1}}, _report(), has_code=lambda _path: True)
    assert found == ["nexy/new.py is never imported by a test"]


def test_a_changed_file_with_no_code_is_not_a_gap():
    assert gate.gaps({"nexy/empty.py": {1}}, _report(), has_code=lambda _path: False) == []


def test_a_module_with_only_a_docstring_has_no_code(tmp_path):
    empty = tmp_path / "empty.py"
    empty.write_text('"""Only a docstring."""\n')
    assert gate.has_code(str(empty)) is False


def test_a_module_with_a_statement_has_code(tmp_path):
    module = tmp_path / "module.py"
    module.write_text('"""Doc."""\nVALUE = 1\n')
    assert gate.has_code(str(module)) is True


def _run(monkeypatch, tmp_path, missing: list[int]) -> int:
    report = tmp_path / "coverage.json"
    measured = {"missing_lines": missing, "missing_branches": []}
    report.write_text(gate.json.dumps(_report(**{"nexy/a.py": measured})))
    monkeypatch.setattr(gate, "_diff", lambda _base: DIFF)
    return gate.main(["--report", str(report)])


def test_the_gate_passes_when_every_added_line_runs(monkeypatch, tmp_path):
    assert _run(monkeypatch, tmp_path, missing=[]) == 0


def test_the_gate_fails_on_an_added_line_no_test_runs(monkeypatch, tmp_path):
    assert _run(monkeypatch, tmp_path, missing=[12]) == 1
