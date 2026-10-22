import shutil
import subprocess
import sys
from pathlib import Path

from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.common.report import print_cmd_result
from nexy.utils.fs.frontmatter import reassemble_frontmatter, split_frontmatter
from nexy.utils.fs.scan import collect_files

_PY_EXTS = (".py",)
_TS_EXTS = (".ts", ".tsx", ".vue", ".svelte")
_NEXY_EXTS = (".nexy", ".mdx")


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
    exe = shutil.which("ruff")
    if not exe:
        console.print(
            f"  [yellow]\u26a0[/yellow] {t('format.skip_tool', 'ruff not found - skipping Python')}"
        )
        return 0
    files = collect_files(root, _PY_EXTS)
    if not files:
        return 0
    args = [exe, "format"]
    if check:
        args.append("--check")
    args.extend(files)
    with console.status("  ruff format ..."):
        r = subprocess.run(args, capture_output=True, text=True)
    print_cmd_result("ruff format", r)
    return 0 if r.returncode == 0 else 1


def _format_ts(root: Path, check: bool) -> int:
    exe = shutil.which("prettier")
    files = collect_files(root, _TS_EXTS)
    if not exe:
        if files:
            msg = t("format.skip_tool", "prettier not found - skipping JS/TS")
            console.print(f"  [yellow]\u26a0[/yellow] {msg}")
        return 0
    if not files:
        return 0
    args = [exe, "--check" if check else "--write", *files]
    with console.status("  prettier ..."):
        r = subprocess.run(args, capture_output=True, text=True)
    print_cmd_result("prettier", r)
    return 0 if r.returncode == 0 else 1


def _format_nexy(root: Path, check: bool) -> int:
    ruff_exe = shutil.which("ruff")
    prettier_exe = shutil.which("prettier")
    files = collect_files(root, _NEXY_EXTS)
    failures = 0
    for f in files:
        try:
            _format_single(Path(f), ruff_exe, prettier_exe, check)
        except Exception as e:
            console.print(f"  [red]\u2718[/red] {f} - {e}")
            failures += 1
    return failures


def _format_single(path: Path, ruff_exe: str | None, prettier_exe: str | None, check: bool) -> None:
    original = path.read_text(encoding="utf-8")
    logic, template = split_frontmatter(original)
    new_logic = _format_logic_block(path, logic, ruff_exe)
    new_template = _format_template_block(path, template, prettier_exe)

    result = reassemble_frontmatter(new_logic, new_template)
    if check:
        if result != original:
            console.print(f"  [red]\u2718[/red] {path}")
            raise RuntimeError("would be reformatted")
        console.print(f"  [green]\u2713[/green] {path}")
    else:
        if result != original:
            path.write_text(result, encoding="utf-8")
            console.print(f"  [green]\u2713[/green] {path}")


def _format_logic_block(path: Path, logic: str, ruff_exe: str | None) -> str:
    if not logic or not ruff_exe:
        return logic
    r = subprocess.run(
        [ruff_exe, "format", "--stdin-filename", "block.py"],
        input=logic,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return r.stdout
    detail = r.stderr.strip().splitlines()
    msg = detail[-1] if detail else f"exit {r.returncode}"
    console.print(f"  [yellow]\u26a0[/yellow] ruff {path} - frontmatter kept as-is ({msg})")
    return logic


def _format_template_block(path: Path, template: str, prettier_exe: str | None) -> str:
    if not template or not prettier_exe:
        return template
    r = subprocess.run(
        [prettier_exe, "--parser", "html", "--stdin-filepath", path.name],
        input=template,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return r.stdout
    if r.stderr:
        detail = r.stderr.strip().splitlines()
        msg = detail[-1] if detail else f"exit {r.returncode}"
        console.print(f"  [yellow]\u26a0[/yellow] prettier {path} - {msg}")
    return template
