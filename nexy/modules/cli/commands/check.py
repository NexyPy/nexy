import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

from nexy.helpers.common.console import console
from nexy.helpers.common.report import print_cmd_result
from nexy.helpers.fs.scan import has_files
from nexy.modules.builder import Builder
from nexy.modules.i18n import t

_PY_EXTS = (".py",)
_TS_EXTS = (".ts", ".tsx", ".vue", ".svelte")
_NEXY_EXTS = (".nexy",)


def check(tsc: bool = True, nexypy: bool = True) -> None:
    """Run type checking across all project files."""
    root = Path.cwd()
    sections: list[tuple[str, bool]] = []

    sections.append(("Python", _check_python(root)))
    if tsc and has_files(root, _TS_EXTS) and shutil.which("tsc"):
        sections.append(("TypeScript", _check_typescript()))
    if nexypy and has_files(root, _NEXY_EXTS):
        sections.append(("Nexy", _check_nexy(root)))

    _print_summary(sections)


def _check_python(root: Path) -> bool:
    if not has_files(root, _PY_EXTS):
        return True
    exe = shutil.which("mypy")
    if not exe:
        skip = t("check.skip_tool", "{tool} not found - skipping {scope}")
        console.print(f"  [yellow]\u26a0[/yellow] {skip.format(tool='mypy', scope='Python')}")
        return True
    with console.status("  mypy ..."):
        r = subprocess.run([exe, str(root)], capture_output=True, text=True)  # nosec B603
    print_cmd_result("mypy", r)
    return r.returncode == 0


def _check_typescript() -> bool:
    tsc_exe = shutil.which("tsc")
    if not tsc_exe:
        skip = t("check.skip_tool", "{tool} not found - skipping {scope}")
        console.print(f"  [yellow]\u26a0[/yellow] {skip.format(tool='tsc', scope='TypeScript')}")
        return True
    with console.status("  tsc ..."):
        r = subprocess.run([tsc_exe, "-b"], capture_output=True, text=True)  # nosec B603/B607
    print_cmd_result("tsc", r)
    return r.returncode == 0


def _check_nexy(root: Path) -> bool:
    ok = True
    with console.status(f"  {t('check.compiling', 'compiling .nexy ...')}"):
        result = Builder().build(showlog=False)
    if result.failed:
        for path in result.failed:
            console.print(f"  [red]\u2718[/red] {path}")
        ok = False

    exe = shutil.which("mypy")
    gen_dir = root / "__nexy__"
    if exe and gen_dir.is_dir():
        with console.status("  mypy __nexy__/ ..."):
            r = subprocess.run([exe, str(gen_dir)], capture_output=True, text=True)  # nosec B603
        print_cmd_result("mypy __nexy__/", r)
        ok = ok and r.returncode == 0
    return ok


def _print_summary(sections: list[tuple[str, bool]]) -> None:
    console.print()
    failed = [name for name, ok in sections if not ok]
    if failed:
        msg = t("check.failed", "{count} section(s) failed").format(count=len(failed))
        console.print(f"  [red]\u2718[/red] {msg}: {', '.join(failed)}")
        sys.exit(1)
    console.print(f"  [green]\u2713[/green] {t('check.passed', 'all checks passed')}")
