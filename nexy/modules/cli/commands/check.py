import shutil
import sys
from pathlib import Path

from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.executables import find_tool
from nexy.helpers.common.messages import error, warning
from nexy.helpers.common.tasks import run_task, step
from nexy.helpers.fs.scan import has_files
from nexy.modules.builder import Builder
from nexy.modules.i18n import t

_PY_EXTS = (".py",)
_TS_EXTS = (".ts", ".tsx", ".vue", ".svelte")
_NEXY_EXTS = (".nexy",)


def check(tsc: bool = True, nexypy: bool = True) -> None:
    """Run type checking across all project files."""
    root = Path.cwd()
    sections: list[tuple[str, bool]] = [("Python", _check_python(root))]
    if tsc and has_files(root, _TS_EXTS) and shutil.which("tsc"):
        sections.append(("TypeScript", _check_typescript()))
    if nexypy and has_files(root, _NEXY_EXTS):
        sections.append(("Nexy", _check_nexy(root)))
    _print_summary(sections)


def _skip(tool: str, scope: str) -> bool:
    """A missing tool is a warning, and its section does not fail."""
    warning(
        t("check.skip_tool", "{tool} not found - skipping {scope}").format(tool=tool, scope=scope)
    )
    return True


def _run_checker(tool: str, scope: str, argv: list[str]) -> bool:
    """One live row while *tool* runs, then one line; a failure keeps its whole report."""
    label = t("check.checking", "Checking {scope} with {tool}").format(scope=scope, tool=tool)
    done = t("check.checked", "Checked {scope} with {tool}").format(scope=scope, tool=tool)
    return run_task(label, argv, done=done, full_output=True).ok


def _check_python(root: Path) -> bool:
    if not has_files(root, _PY_EXTS):
        return True
    exe = find_tool("mypy")
    if not exe:
        return _skip("mypy", "Python")
    return _run_checker("mypy", "Python", [exe, str(root)])


def _check_typescript() -> bool:
    tsc_exe = shutil.which("tsc")
    if not tsc_exe:
        return _skip("tsc", "TypeScript")
    return _run_checker("tsc", "TypeScript", [tsc_exe, "-b"])


def _check_nexy(root: Path) -> bool:
    compiling = t("check.compiling", "Compiling the .nexy files")
    with step(compiling, done=t("check.compiled", "Compiled the .nexy files")):
        result = Builder().build(showlog=False)
    for path in result.failed:
        error(t("check.not_compiled", "Could not compile {path}").format(path=escape(str(path))))
    exe = find_tool("mypy")
    generated = root / "__nexy__"
    if not (exe and generated.is_dir()):
        return not result.failed
    return _run_checker("mypy", "__nexy__", [exe, str(generated)]) and not result.failed


def _print_summary(sections: list[tuple[str, bool]]) -> None:
    failed = [name for name, ok in sections if not ok]
    if failed:
        count = t("check.failed", "{count} section(s) failed").format(count=len(failed))
        error(count, cause=", ".join(failed))
        sys.exit(1)
    console.print(t("check.passed", "All checks passed"))
