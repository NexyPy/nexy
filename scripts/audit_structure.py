"""Measure the structure rules of AGENTS.md: small functions, small classes, no copied code.

    python scripts/audit_structure.py                 # report every offender
    python scripts/audit_structure.py --check         # fail on a new or worse offender
    python scripts/audit_structure.py --write         # record today's offenders as the baseline

The baseline (`scripts/structure_baseline.json`) lists the offenders that exist today. `--check`
accepts those and nothing else, so the numbers can only go down: a function that is split leaves
the baseline, and a new long function, class or copy fails the gate.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "scripts" / "structure_baseline.json"
SKIPPED_PARTS = {"templates", "__pycache__", ".venv", "node_modules", "__nexy__"}
NOT_CODE_STARTS = ("import ", "from ", "#", '"""', "'''", "@")


@dataclass(frozen=True)
class Limits:
    function: int = 20
    methods: int = 10
    file: int = 400
    duplicate_window: int = 8


@dataclass(frozen=True)
class Finding:
    """One offender: what kind, where, its name and its measure (lines or methods)."""

    kind: str
    path: str
    name: str
    value: int
    ident: str = ""

    @property
    def key(self) -> str:
        return self.ident or f"{self.kind}:{self.path}:{self.name}"


def read_sources(root: Path) -> dict[str, str]:
    """Every Python file under *root* worth auditing, by POSIX path relative to *root*."""
    sources = {}
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root)
        if not SKIPPED_PARTS.intersection(relative.parts):
            sources[relative.as_posix()] = path.read_text(encoding="utf-8")
    return sources


def _body_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Lines of the body, without its docstring."""
    body = node.body
    first = body[0]
    is_docstring = isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
    if is_docstring and isinstance(first.value.value, str) and len(body) > 1:  # type: ignore[attr-defined]
        first = body[1]
    return (node.end_lineno or node.lineno) - first.lineno + 1


def _definitions(
    tree: ast.AST, scope: str = ""
) -> Iterator[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef]]:
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            name = f"{scope}{node.name}"
            yield name, node
            yield from _definitions(node, f"{name}.")
        else:
            yield from _definitions(node, scope)


def definition_findings(path: str, tree: ast.AST, limits: Limits) -> list[Finding]:
    found = []
    for name, node in _definitions(tree):
        if isinstance(node, ast.ClassDef):
            count = sum(isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) for n in node.body)
            if count > limits.methods:
                found.append(Finding("class", path, name, count))
        elif (length := _body_length(node)) > limits.function:
            found.append(Finding("function", path, name, length))
    return found


def file_findings(path: str, source: str, limits: Limits) -> list[Finding]:
    lines = len(source.splitlines())
    return [Finding("file", path, path, lines)] if lines > limits.file else []


def _code_lines(source: str) -> list[tuple[int, str]]:
    """(line number, stripped text) of the lines that carry code a copy would repeat."""
    rows = [(n, text.strip()) for n, text in enumerate(source.splitlines(), 1)]
    return [(n, text) for n, text in rows if len(text) > 3 and not text.startswith(NOT_CODE_STARTS)]


def _windows(path: str, source: str, size: int) -> Iterator[tuple[str, str, int, int]]:
    """(window text, path, line, index among the code lines) for every run of *size* lines."""
    code = _code_lines(source)
    for index in range(len(code) - size + 1):
        yield "\n".join(text for _, text in code[index : index + size]), path, code[index][0], index


def _matches(
    sources: dict[str, str], size: int
) -> dict[tuple[str, str, int], list[tuple[int, int, str]]]:
    """Pairs of places that share a window: (first path, second path, offset) -> positions."""
    seen: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for path, source in sources.items():
        for text, name, line, index in _windows(path, source, size):
            seen[text].append((name, line, index))
    pairs: dict[tuple[str, str, int], list[tuple[int, int, str]]] = defaultdict(list)
    for text, places in seen.items():
        for (a, line_a, i), (b, _line_b, j) in zip(places, places[1:], strict=False):
            if a != b or abs(i - j) >= size:
                pairs[(a, b, i - j)].append((i, line_a, text))
    return pairs


def _blocks(positions: list[tuple[int, int, str]], size: int) -> Iterator[tuple[int, int, str]]:
    """Merge consecutive windows into blocks: (first line, lines long, first window text)."""
    run: list[tuple[int, int, str]] = []
    for position in sorted(positions):
        if run and position[0] != run[-1][0] + 1:
            yield run[0][1], len(run) + size - 1, run[0][2]
            run = []
        run.append(position)
    if run:
        yield run[0][1], len(run) + size - 1, run[0][2]


def duplicate_findings(sources: dict[str, str], size: int) -> list[Finding]:
    found = []
    for (first, second, _offset), positions in _matches(sources, size).items():
        for line, length, text in _blocks(positions, size):
            ident = "duplicate:" + hashlib.sha1(text.encode()).hexdigest()[:10]  # noqa: S324
            found.append(Finding("duplicate", f"{first}:{line}", f"{second}", length, ident))
    return found


def audit(root: Path, limits: Limits | None = None) -> list[Finding]:
    limits = limits or Limits()
    sources = read_sources(root)
    found: list[Finding] = []
    for path, source in sources.items():
        found += definition_findings(path, ast.parse(source), limits)
        found += file_findings(path, source, limits)
    found += duplicate_findings(sources, limits.duplicate_window)
    return found


def to_baseline(found: list[Finding]) -> dict[str, int]:
    return {finding.key: finding.value for finding in found}


def new_findings(found: list[Finding], baseline: dict[str, int]) -> list[Finding]:
    """The offenders the baseline does not allow: new ones, and ones that got worse."""
    return [f for f in found if f.key not in baseline or f.value > baseline[f.key]]


def _print_report(found: list[Finding]) -> None:
    counts: dict[str, int] = defaultdict(int)
    for finding in sorted(found, key=lambda f: (f.kind, -f.value)):
        counts[finding.kind] += 1
        print(f"{finding.kind:9} {finding.value:5}  {finding.path}  {finding.name}")
    print("\n" + ", ".join(f"{kind}: {count}" for kind, count in sorted(counts.items())))


def _parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="fail on a new or worse offender")
    parser.add_argument("--write", action="store_true", help="record the offenders as the baseline")
    parser.add_argument("--root", type=Path, default=ROOT / "nexy")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse(sys.argv[1:] if argv is None else argv)
    found = audit(args.root)
    if args.write:
        BASELINE.write_text(json.dumps(to_baseline(found), indent=1, sort_keys=True) + "\n")
        print(f"baseline written: {len(found)} offenders")
        return 0
    if not args.check:
        _print_report(found)
        return 0
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    worse = new_findings(found, baseline)
    _print_report(worse)
    return 1 if worse else 0


if __name__ == "__main__":
    raise SystemExit(main())
