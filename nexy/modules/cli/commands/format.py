import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

from nexy.helpers.common.console import console
from nexy.helpers.common.executables import find_tool
from nexy.helpers.common.report import print_cmd_result
from nexy.helpers.fs.frontmatter import reassemble_frontmatter, split_frontmatter
from nexy.helpers.fs.nexy_format import FormatError, format_logic, format_template
from nexy.helpers.fs.scan import collect_files
from nexy.modules.i18n import t

_PY_EXTS = (".py",)
_TS_EXTS = (".ts", ".tsx", ".vue", ".svelte", ".mdx")
_NEXY_EXTS = (".nexy",)


def format_(check: bool = False) -> None:
    """Auto-format all project files."""
    root = Path.cwd()
    failures = 0

    failures += _format_python(root, check)
    failures += _format_ts(root, check)
    failures += _format_nexy(root, check)

    console.print()
    if failures:
        msg = t("format.failed", "{count} file(s) failed").format(count=failures)
        console.print(f"  [red]\u2718[/red] {msg}")
        sys.exit(1)
    console.print(f"  [green]\u2713[/green] {t('format.passed', 'formatting complete')}")


def _format_python(root: Path, check: bool) -> int:
    exe = find_tool("ruff")
    if not exe:
        skip = t("format.skip_tool", "{tool} not found - skipping {scope}")
        console.print(f"  [yellow]\u26a0[/yellow] {skip.format(tool='ruff', scope='Python')}")
        return 0
    files = collect_files(root, _PY_EXTS)
    if not files:
        return 0
    args = [exe, "format"]
    if check:
        args.append("--check")
    args.extend(files)
    with console.status("  ruff format ..."):
        r = subprocess.run(args, capture_output=True, text=True)  # nosec B603
    print_cmd_result("ruff format", r)
    return 0 if r.returncode == 0 else 1


def _format_ts(root: Path, check: bool) -> int:
    exe = shutil.which("prettier")
    files = collect_files(root, _TS_EXTS)
    if not exe:
        if files:
            msg = t("format.skip_tool", "{tool} not found - skipping {scope}")
            console.print(f"  [yellow]\u26a0[/yellow] {msg.format(tool='prettier', scope='JS/TS')}")
        return 0
    if not files:
        return 0
    args = [exe, "--check" if check else "--write", *files]
    with console.status("  prettier ..."):
        r = subprocess.run(args, capture_output=True, text=True)  # nosec B603
    print_cmd_result("prettier", r)
    return 0 if r.returncode == 0 else 1


def _format_nexy(root: Path, check: bool) -> int:
    ruff_exe = find_tool("ruff")
    prettier_exe = shutil.which("prettier")
    failures = 0
    for name in collect_files(root, _NEXY_EXTS):
        try:
            _format_single(Path(name), ruff_exe, prettier_exe, check)
        except (FormatError, RuntimeError, OSError) as error:
            console.print(f"  [red]✘[/red] {name} - {error}")
            failures += 1
    return failures


def formatted_source(
    path: Path, source: str, ruff_exe: str | None, prettier_exe: str | None
) -> str:
    """The canonical text of a .nexy file."""
    logic, template = split_frontmatter(source)
    text = reassemble_frontmatter(
        format_logic(logic, ruff_exe), format_template(template, prettier_exe, path.name)
    )
    return text.rstrip() + "\n"


def _format_single(path: Path, ruff_exe: str | None, prettier_exe: str | None, check: bool) -> None:
    original = path.read_text(encoding="utf-8")
    result = formatted_source(path, original, ruff_exe, prettier_exe)
    if check and result != original:
        raise RuntimeError("would be reformatted")
    if result != original:
        path.write_text(result, encoding="utf-8")
    console.print(f"  [green]✓[/green] {path}")
