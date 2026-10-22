import os
from collections.abc import Iterable, Iterator
from pathlib import Path

# Canonical skip list for every source-tree walk in the framework.
# builders, routers and CLI probes all prune the same noise here instead of
# keeping private copies of this set in sync.
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "__nexy__",
    ".nexy-virt",
    ".pytest_cache",
    ".mypy_cache",
    ".uvcache",
    "dist",
    "build",
    ".vscode",
    ".vscode-test",
    ".github",
    ".cursor",
}


def walk_paths(
    root: Path | str, suffixes: Iterable[str], excluded: set[str] = SKIP_DIRS
) -> Iterator[Path]:
    """Yield files with one of *suffixes* under *root* (DFS order), pruning
    directory names listed in *excluded*.

    Practically a shared implementation for has_files/collect_files and the
    builder/route discovery classes so only one tree-walker exists.
    """
    normalized = {s if s.startswith(".") else f".{s}" for s in suffixes}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excluded]
        for name in filenames:
            if os.path.splitext(name)[1] in normalized:
                yield Path(dirpath) / name


def has_files(root: Path, exts: tuple[str, ...]) -> bool:
    """Return True when at least one file ending in *exts* exists under *root*."""
    for _ in walk_paths(root, exts, excluded=set(SKIP_DIRS)):
        return True
    return False


def collect_files(root: Path, exts: tuple[str, ...]) -> list[str]:
    """List every file ending in *exts* under *root*, sorted, skipping SKIP_DIRS."""
    return sorted(str(match) for match in walk_paths(root, exts, excluded=set(SKIP_DIRS)))
