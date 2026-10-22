from pathlib import Path


def format_size(byte_count: int) -> str:
    """Human readable size: 512B, 4.2kB, 1.5MB."""
    if byte_count < 1024:
        return f"{byte_count}B"
    if byte_count < 1024 * 1024:
        return f"{byte_count / 1024:.1f}kB"
    return f"{byte_count / (1024 * 1024):.1f}MB"


def artifact_size(filepath: str) -> str:
    """Size label of the rendered artifact for *filepath* ('' when it is missing)."""
    base = Path(filepath)
    html_path = Path("__nexy__/client/static") / base.parent / f"{base.stem}.Default.html"
    if html_path.exists():
        return format_size(html_path.stat().st_size)
    if base.exists():
        return format_size(base.stat().st_size)
    return ""
