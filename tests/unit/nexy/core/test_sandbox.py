import pytest

from nexy.core.sandbox import sandboxed_exec


def test_sandbox_simple_execution() -> None:
    ns: dict[str, object] = {"x": 1}
    sandboxed_exec("y = x + 1", ns)
    assert ns.get("y") == 2


def test_sandbox_disallows_import() -> None:
    with pytest.raises(ImportError):
        sandboxed_exec("import os", {})


def test_sandbox_disallows_open() -> None:
    with pytest.raises(NameError):
        sandboxed_exec("open('/etc/passwd')", {})


def test_sandbox_disallows_exec_nested() -> None:
    with pytest.raises(NameError):
        sandboxed_exec("exec('x=1')", {})


def test_sandbox_disallows_eval() -> None:
    with pytest.raises(NameError):
        sandboxed_exec("eval('1+1')", {})


def test_sandbox_disallows_compile() -> None:
    with pytest.raises(NameError):
        sandboxed_exec("compile('x=1', '<test>', 'exec')", {})


def test_sandbox_allows_builtin_sum() -> None:
    ns: dict[str, object] = {}
    sandboxed_exec("result = sum([1, 2, 3])", ns)
    assert ns.get("result") == 6


def test_sandbox_allows_builtin_len() -> None:
    ns: dict[str, object] = {}
    sandboxed_exec("result = len([1, 2, 3])", ns)
    assert ns.get("result") == 3


def test_sandbox_allows_builtin_range() -> None:
    ns: dict[str, object] = {}
    sandboxed_exec("result = list(range(3))", ns)
    assert ns.get("result") == [0, 1, 2]
