import shutil
import sys
from pathlib import Path

from rich.markup import escape

from nexy.helpers.common.console import console
from nexy.helpers.common.executables import find_tool
from nexy.helpers.common.messages import error, warning
from nexy.helpers.common.tasks import run_task, step
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
    failures = _format_python(root, check) + _format_ts(root, check) + _format_nexy(root, check)
    if failures:
        error(t("format.failed", "{count} file(s) failed").format(count=failures))
        sys.exit(1)
    console.print(t("format.passed", "All files formatted"))


def _skip(tool: str, scope: str) -> int:
    """A missing tool is a warning, and its files do not fail."""
    warning(
        t("format.skip_tool", "{tool} not found - skipping {scope}").format(tool=tool, scope=scope)
    )
    return 0


def _run_formatter(tool: str, scope: str, argv: list[str], check: bool) -> int:
    """One live row while *tool* runs, then one line; a failure keeps what the tool said."""
    if check:
        label = t("format.checking", "Checking the format of {scope} with {tool}")
        done = t("format.checked", "Checked the format of {scope} with {tool}")
    else:
        label = t("format.formatting", "Formatting {scope} with {tool}")
        done = t("format.formatted", "Formatted {scope} with {tool}")
    names = {"scope": scope, "tool": tool}
    ok = run_task(label.format(**names), argv, done=done.format(**names), full_output=True).ok
    return 0 if ok else 1


def _format_python(root: Path, check: bool) -> int:
    exe = find_tool("ruff")
    if not exe:
        return _skip("ruff", "Python")
    files = collect_files(root, _PY_EXTS)
    if not files:
        return 0
    return _run_formatter(
        "ruff", "Python", [exe, "format", *(["--check"] if check else []), *files], check
    )


def _format_ts(root: Path, check: bool) -> int:
    exe = shutil.which("prettier")
    files = collect_files(root, _TS_EXTS)
    if not files:
        return 0
    if not exe:
        return _skip("prettier", "JS/TS")
    return _run_formatter(
        "prettier", "JS/TS", [exe, "--check" if check else "--write", *files], check
    )


def _format_nexy(root: Path, check: bool) -> int:
    """One line for all the .nexy files; each one that fails is a uv error."""
    files = collect_files(root, _NEXY_EXTS)
    if not files:
        return 0
    ruff_exe, prettier_exe = find_tool("ruff"), shutil.which("prettier")
    label = t("format.nexy", "Formatting {count} .nexy file(s)").format(count=len(files))
    done = t("format.nexy_done", "Formatted {count} .nexy file(s)").format(count=len(files))
    failed: list[tuple[str, str]] = []
    with step(label, done=done):
        for name in files:
            try:
                _format_single(Path(name), ruff_exe, prettier_exe, check)
            except (FormatError, RuntimeError, OSError) as exc:
                failed.append((name, str(exc)))
    for name, reason in failed:
        error(escape(_shown(root, name)), cause=escape(reason))
    return len(failed)


def _shown(root: Path, name: str) -> str:
    """*name* relative to the project, as a person reads it."""
    path = Path(name)
    return str(path.relative_to(root)) if path.is_absolute() and path.is_relative_to(root) else name


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
