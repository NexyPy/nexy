from nexy.errors import NexyCompileError
from nexy.modules.builder import BuildError


def test_compile_error_str_includes_hint() -> None:
    error = NexyCompileError("a.nexy", "boom", 2, 3, "do the thing")
    assert "a.nexy:2:3 - boom" in str(error)
    assert str(error).endswith("Fix: do the thing")


def test_compile_error_str_without_hint_stays_compact() -> None:
    assert str(NexyCompileError("a.nexy", "boom")) == "a.nexy - boom"


def test_build_error_format_includes_hint() -> None:
    error = BuildError(path="a.nexy", message="boom", line=1, hint="do the thing")
    assert error.format().endswith("Fix: do the thing")


def test_build_error_format_without_hint_stays_compact() -> None:
    assert BuildError(path="a.nexy", message="boom").format() == "a.nexy - [Exception] boom"
