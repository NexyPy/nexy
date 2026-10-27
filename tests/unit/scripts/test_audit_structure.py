"""scripts/audit_structure.py measures the structure rules of AGENTS.md."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "audit_structure.py"


def _load() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("audit_structure", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their annotations through it
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="audit")
def _audit() -> types.ModuleType:
    return _load()


def _long_function(name: str, lines: int) -> str:
    body = "\n".join(f"    value_{n} = {n}" for n in range(lines))
    return f"def {name}():\n{body}\n"


def _project(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, source in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    return tmp_path


class TestFunctions:
    def test_a_function_over_the_limit_is_reported(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("big", 25)})
        found = audit.audit(root, audit.Limits(function=20))
        assert [(f.kind, f.name, f.value) for f in found] == [("function", "big", 25)]

    def test_a_function_at_the_limit_is_not(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("ok", 20)})
        assert audit.audit(root, audit.Limits(function=20)) == []

    def test_the_docstring_does_not_count(self, audit, tmp_path):
        source = 'def f():\n    """One.\n\n    Two.\n    """\n' + "\n".join(
            f"    v{n} = {n}" for n in range(20)
        )
        root = _project(tmp_path, {"a.py": source + "\n"})
        assert audit.audit(root, audit.Limits(function=20)) == []

    def test_a_method_is_named_with_its_class(self, audit, tmp_path):
        body = "\n".join(f"        v{n} = {n}" for n in range(25))
        root = _project(tmp_path, {"a.py": f"class K:\n    def run(self):\n{body}\n"})
        names = [f.name for f in audit.audit(root, audit.Limits(function=20))]
        assert names == ["K.run"]


class TestClasses:
    def test_a_class_with_too_many_methods_is_reported(self, audit, tmp_path):
        methods = "\n".join(f"    def m{n}(self):\n        pass\n" for n in range(11))
        root = _project(tmp_path, {"a.py": f"class Big:\n{methods}"})
        found = audit.audit(root, audit.Limits(methods=10))
        assert [(f.kind, f.name, f.value) for f in found] == [("class", "Big", 11)]


class TestFiles:
    def test_a_file_over_the_limit_is_reported(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": "x = 1\n" * 30})
        found = audit.audit(root, audit.Limits(file=20))
        assert [(f.kind, f.value) for f in found] == [("file", 30)]


class TestDuplicates:
    SHARED = (
        "    first = compute_first_value(argument)\n"
        "    second = compute_second_value(first)\n"
        "    third = combine(first, second)\n"
        "    log_result(third, destination)\n"
        "    store_result(third, destination)\n"
        "    return finish(third)\n"
    )

    def test_the_same_block_in_two_files_is_reported(self, audit, tmp_path):
        root = _project(
            tmp_path,
            {
                "a.py": f"def one(argument):\n{self.SHARED}",
                "b.py": f"def two(argument):\n{self.SHARED}",
            },
        )
        found = audit.audit(root, audit.Limits(duplicate_window=6))
        assert [f.kind for f in found] == ["duplicate"]

    def test_the_report_names_both_places(self, audit, tmp_path):
        root = _project(
            tmp_path,
            {
                "a.py": f"def one(argument):\n{self.SHARED}",
                "b.py": f"def two(argument):\n{self.SHARED}",
            },
        )
        found = audit.audit(root, audit.Limits(duplicate_window=6))
        assert "a.py" in found[0].path and "b.py" in found[0].name

    def test_different_code_is_not_a_duplicate(self, audit, tmp_path):
        other = self.SHARED.replace("first", "alpha").replace("second", "beta")
        root = _project(
            tmp_path,
            {"a.py": f"def one(argument):\n{self.SHARED}", "b.py": f"def two(argument):\n{other}"},
        )
        assert audit.audit(root, audit.Limits(duplicate_window=6)) == []

    def test_imports_alone_are_not_a_duplicate(self, audit, tmp_path):
        imports = "".join(f"import module_number_{n}\n" for n in range(8))
        root = _project(tmp_path, {"a.py": imports, "b.py": imports})
        assert audit.audit(root, audit.Limits(duplicate_window=6)) == []


class TestBaseline:
    def test_a_known_offender_passes(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("big", 25)})
        found = audit.audit(root, audit.Limits(function=20))
        baseline = audit.to_baseline(found)
        assert audit.new_findings(found, baseline) == []

    def test_a_new_offender_fails(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("big", 25)})
        found = audit.audit(root, audit.Limits(function=20))
        assert audit.new_findings(found, {}) == found

    def test_an_offender_that_got_longer_fails(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("big", 25)})
        found = audit.audit(root, audit.Limits(function=20))
        baseline = {key: value - 5 for key, value in audit.to_baseline(found).items()}
        assert audit.new_findings(found, baseline) == found

    def test_the_baseline_is_json(self, audit, tmp_path):
        root = _project(tmp_path, {"a.py": _long_function("big", 25)})
        found = audit.audit(root, audit.Limits(function=20))
        assert json.loads(json.dumps(audit.to_baseline(found)))

    def test_templates_are_not_audited(self, audit, tmp_path):
        root = _project(tmp_path, {"templates/a.py": _long_function("big", 25)})
        assert audit.audit(root, audit.Limits(function=20)) == []
