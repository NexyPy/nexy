"""The list a build leaves: one line of counts, then the files it made, as uv lists packages."""

from __future__ import annotations

import io

from rich.console import Console

from nexy.helpers.common.summary import print_summary


def _print(*args, **kwargs) -> str:
    out = Console(file=io.StringIO(), width=100)
    print_summary(*args, console=out, **kwargs)
    return out.file.getvalue()


def test_summary_starts_with_the_title_and_the_counts():
    text = _print("Server components", ["2 built", "1 cached"], ["a.nexy", "b.nexy"])
    assert text.splitlines()[0] == "Server components: 2 built, 1 cached"


def test_summary_lists_each_file_with_a_plus():
    text = _print("Routes", ["1 built"], ["src/routes/index.tsx"])
    assert text.splitlines()[1] == " + src/routes/index.tsx"


def test_summary_shows_three_files_then_how_many_more():
    files = [f"f{n}.nexy" for n in range(5)]
    text = _print("Routes", ["5 built"], files, more="and {count} more")
    assert text.splitlines()[4] == "   and 2 more"


def test_summary_of_nothing_is_only_the_counts():
    assert _print("Routes", ["0 built"], []) == "Routes: 0 built\n"


def test_summary_draws_no_tree_and_no_mark():
    text = _print("Routes", ["5 built"], [f"f{n}" for n in range(5)])
    assert not set(text) & set("├└│─✓✗✘")
