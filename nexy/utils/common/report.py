import subprocess  # nosec B404

from nexy.utils.common.console import console
from nexy.utils.common.formatting import artifact_size

_MAX_SHOWN = 3


def print_cmd_result(name: str, result: subprocess.CompletedProcess[str]) -> None:
    """Print a one-line pass/fail verdict for a finished command."""
    if result.returncode == 0:
        console.print(f"  [green]\u2713[/green] {name}")
        return
    console.print(f"  [red]\u2718[/red] {name}")
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]")


def print_tree_section(
    title: str,
    success: list[str],
    failed: list[str],
    ok_style: str,
    fail_style: str,
    skipped: list[str] | None = None,
    labels: dict[str, str] | None = None,
) -> None:
    """Print a grouped tree of results (skipped/success/failed) under *title*.

    *labels* overrides the default group captions (kept caller-side so this
    module stays free of i18n).
    """
    captions = {
        "skipped": "Skipped (cached)",
        "success": "Build success",
        "failed": "Build Failed",
        **(labels or {}),
    }

    total = len(success) + len(failed) + (len(skipped) if skipped else 0)
    console.print(f"\n{title} [{total}]")
    console.print("[dim]\u2502[/dim]")

    groups: list[tuple[str, list[str], str, str]] = []
    if skipped:
        groups.append((captions["skipped"], skipped, "dim", "="))
    groups.extend(
        [
            (captions["success"], success, ok_style, "\u2713"),
            (captions["failed"], failed, fail_style, "\u2717"),
        ]
    )

    for gi, (gname, gfiles, gstyle, mark) in enumerate(groups):
        is_last_group = gi == len(groups) - 1
        gprefix = "\u2514\u2500\u2500" if is_last_group else "\u251c\u2500\u2500"
        console.print(f"[dim]{gprefix} {gname} [{len(gfiles)}][/dim]")
        _print_group_files(gfiles, gstyle, mark)
        if not is_last_group:
            console.print("[dim]\u2502[/dim]")


def _print_group_files(files: list[str], style: str, mark: str) -> None:
    shown = files[:_MAX_SHOWN]
    has_more = len(files) > _MAX_SHOWN

    for fi, f in enumerate(shown):
        is_last_item = fi == len(shown) - 1 and not has_more
        stem = "\u2514\u2500\u2500" if is_last_item else "\u251c\u2500\u2500"
        prefix = f"\u2502   {stem}"
        size = artifact_size(f)
        size_display = f"  [{size}]" if size else ""
        console.print(f"[dim]{prefix} {fi + 1}. {f}{size_display}[/dim] [{style}]{mark}[/]")

    if has_more:
        more = len(files) - _MAX_SHOWN
        console.print(f"[dim]\u2502   \u2514\u2500\u2500 [{more} more][/dim]")
