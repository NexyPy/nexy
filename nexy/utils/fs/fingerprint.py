from pathlib import Path


def stat_fingerprint(path: Path) -> str:
    """Fast change fingerprint of *path*: 'mtime_ns:size' (no content hash)."""
    try:
        stat = path.stat()
        return f"{stat.st_mtime_ns}:{stat.st_size}"
    except OSError:
        return ""


def first_stat_fingerprint(names: tuple[str, ...]) -> str:
    """Fingerprint of the first existing file among *names* ('' when none)."""
    for name in names:
        path = Path(name)
        if path.is_file():
            stat = path.stat()
            return f"{name}:{stat.st_mtime_ns}:{stat.st_size}"
    return ""
