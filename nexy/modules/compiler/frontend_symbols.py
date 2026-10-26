"""What a framework route file exports, and where its client and SSG files live."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

_TSX_EXPORT_RE = re.compile(
    r"export\s+(?:default\s+)?(?:function|const|class|let|var)\s+([A-Za-z_$][\w$]*)"
)
_TSX_EXPORT_DEFAULT_RE = re.compile(r"export\s+default\s")


def detect_mdx_framework(src: Path) -> str:
    """Auto-detect React vs Preact for an .mdx file by inspecting imports."""
    try:
        content = src.read_text(encoding="utf-8")
    except OSError:
        return "react"
    if "from 'preact'" in content or 'from "preact"' in content:
        return "preact"
    return "react"


def resolve_tsx_export_symbol(src: Path, fallback_stem: str) -> str:
    """Resolve the actual TSX export symbol for a React/Preact route file.

    Priority:
      1. `export default X` -> "default"
      2. First `export function|const|class X` -> "X"
      3. Fallback: PascalCase of file stem (card.tsx -> Card), else "Default"
    """
    try:
        content = src.read_text(encoding="utf-8")
    except OSError:
        content = ""

    if _TSX_EXPORT_DEFAULT_RE.search(content):
        return "default"
    match = _TSX_EXPORT_RE.search(content)
    if match:
        return match.group(1)

    stem = fallback_stem.strip()
    if stem:
        cleaned = re.sub(r"[^a-zA-Z0-9_$]+", "", stem)
        if cleaned:
            first = cleaned[0].upper() if cleaned[0].isalpha() else cleaned[0]
            rest = cleaned[1:] if len(cleaned) > 1 else ""
            return f"{first}{rest}"
    return "Default"


def resolve_symbol(src: Path, ext: str, stem: str) -> str:
    """Pick the client-side export symbol to hydrate for this route file."""
    if ext in (".vue", ".svelte"):
        return "default"
    if ext == ".mdx":
        return "default"
    return resolve_tsx_export_symbol(src, stem)


def glob_ref(src: Path, posix_src: str) -> tuple[str, str]:
    """(import.meta.glob path, md5 key) for one framework route source."""
    try:
        cwd = Path.cwd()
        rel_from_cwd = "/" + src.resolve().relative_to(cwd).as_posix().lstrip("/")
    except ValueError:
        rel_from_cwd = "/" + posix_src.lstrip("/")
    key_hash = hashlib.md5(rel_from_cwd.encode("utf-8"), usedforsecurity=False).hexdigest()
    return rel_from_cwd, key_hash


def ssg_static_path(rel_glob: str, framework: str, symbol: str) -> str:
    """SSG HTML path: same convention as NexyClientComponent._get_static_content.

    Vue/Svelte: __nexy__/client/static/<path>.html  (default export)
    TSX (React):  __nexy__/client/static/<path-without-tsx>.Default.html
    """
    if framework in ("vue", "svelte"):
        rel_path_html = rel_glob + ".html"
    else:
        export_name = "Default" if symbol == "default" else symbol
        rel_path_html = rel_glob.replace(".tsx", "").replace(".mdx", "") + f".{export_name}.html"
    return f"__nexy__/client/static{rel_path_html}"
