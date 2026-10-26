"""The small decisions of the parser: error positions, phases that fail together, known tags."""

from __future__ import annotations

import pytest

from nexy.core.models import LogicResult, NexyImport
from nexy.errors import NexyCompileError, error_position
from nexy.modules.compiler.parser import (
    _attempt,
    _capitalised_python_imports,
    _compile_error,
    _names_of_nexy_imports,
)


class TestErrorPosition:
    def test_a_syntax_error_has_a_line_and_a_column(self):
        try:
            compile("def f(:\n", "x", "exec")
        except SyntaxError as failure:
            assert error_position(failure) == (1, 7)

    def test_a_nexy_error_has_a_line_and_a_column(self):
        failure = NexyCompileError("a.nexy", "bad", line=3, column=5)
        assert error_position(failure) == (3, 5)

    def test_a_plain_error_has_neither(self):
        assert error_position(ValueError("x")) == (None, None)


class TestAttempt:
    def test_a_result_is_returned(self):
        failures: list[Exception] = []
        assert _attempt(lambda: 7, failures) == 7 and failures == []

    def test_a_failure_is_recorded_and_not_raised(self):
        failures: list[Exception] = []

        def boom() -> int:
            raise ValueError("no")

        assert _attempt(boom, failures) is None and len(failures) == 1


class TestCompileError:
    def test_one_failure_keeps_its_message_and_position(self):
        error = _compile_error("a.nexy", [NexyCompileError("a.nexy", "bad", line=2, column=1)])
        assert (error.message, error.line, error.column) == ("a.nexy:2:1 - bad", 2, 1)

    def test_several_failures_are_listed_together(self):
        error = _compile_error("a.nexy", [ValueError("first"), ValueError("second")])
        assert "2 errors found" in error.message and "first" in error.message
        assert "second" in error.message

    def test_several_failures_say_to_fix_each(self):
        error = _compile_error("a.nexy", [ValueError("a"), ValueError("b")])
        assert error.hint is not None and "each" in error.hint


class TestKnownComponents:
    @staticmethod
    def _logic(*imports: NexyImport) -> LogicResult:
        return LogicResult(python_code="", props=[], nexy_imports=list(imports), css_imports=[])

    def test_the_alias_wins_over_the_symbol(self):
        imp = NexyImport(path="./a.nexy", symbol="A", alias="Card")
        assert _names_of_nexy_imports(self._logic(imp)) == {"Card"}

    def test_the_symbol_is_used_without_an_alias(self):
        imp = NexyImport(path="./a.nexy", symbol="A", alias=None)
        assert _names_of_nexy_imports(self._logic(imp)) == {"A"}

    def test_only_capitalised_python_imports_are_tags(self):
        code = "from ui import Button, helper as Util, other\n"
        assert _capitalised_python_imports(code) == {"Button", "Util"}

    def test_code_that_does_not_parse_has_none(self):
        assert _capitalised_python_imports("def (:") == set()


@pytest.mark.parametrize("code", ["", "x = 1"])
def test_code_without_imports_has_no_tags(code):
    assert _capitalised_python_imports(code) == set()
