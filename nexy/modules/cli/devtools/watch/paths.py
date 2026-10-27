"""Which paths the dev server reacts to, and what kind of path each one is."""

from __future__ import annotations

from pathlib import Path

from nexy.core.config import Config

_IGNORED_FRAGMENTS = (
    ".git/",
    "venv",
    "/venv",
    ".venv/",
    "/.venv",
    "__nexy__/",
    "/__nexy__",
    ".nexy-virt/",
    "/.nexy-virt",
    "__pycache__/",
    "node_modules/",
)


def normalize_path(raw: str | bytes) -> str:
    """POSIX-style path relative to the current working directory."""
    text = (raw.decode() if isinstance(raw, bytes) else raw).replace("\\", "/")
    cwd = Path.cwd().as_posix()
    if text.startswith(cwd):
        text = text[len(cwd) + 1 :]
    # Strip only the literal "./" prefix: lstrip("./") would also eat the leading "/" of absolute
    # paths outside the working directory and the leading dot of dotfiles.
    return text.removeprefix("./")


def is_ignored_path(path: str) -> bool:
    """True for paths a rebuild should never react to."""
    if any(fragment in path for fragment in _IGNORED_FRAGMENTS):
        return True
    # excludeDirs (docs, templates, ...) are checked here: glob exclusions such as "**/docs/**"
    # do not match root-level directories with PurePath.match.
    posix = f"/{path}"
    return any(f"/{name}/" in posix for name in Config().excludeDirs)


def is_generated_init(path: str) -> bool:
    """True for an empty ``__init__.py``: the file Nexy creates itself, not an edit to react to."""
    if Path(path).name != "__init__.py":
        return False
    try:
        return Path(path).stat().st_size == 0
    except OSError:
        return False


def is_stray_markdown(path: str) -> bool:
    """True for a Markdown file of the project outside the routes, like README.md: not a page."""
    if Path(path).suffix not in (".md", ".mdx") or Path(path).is_absolute():
        return False
    return not path.startswith(f"{Config.ROUTER_PATH.strip('/')}/")


def is_route_page(path: str) -> bool:
    """True for a page of the routes directory that is not Python (``.nexy``, ``.md``, ``.tsx``...).

    The route table is built when the server starts, so a page that appears, disappears or moves
    needs a restart; editing one only needs a recompile.
    """
    routes = f"{Config.ROUTER_PATH.strip('/')}/"
    suffix = Path(path).suffix
    return (
        path.startswith(routes)
        and suffix != ".py"
        and suffix in Config.ROUTE_FILE_EXTENSIONS
        and not is_ignored_path(path)
    )


def is_routes_directory(path: str) -> bool:
    """True for the routes directory or one of its subdirectories."""
    routes = Config.ROUTER_PATH.strip("/")
    return (path == routes or path.startswith(f"{routes}/")) and not is_ignored_path(path)


def needs_restart(path: str) -> bool:
    """True for server-side files whose change requires a reload."""
    return path.endswith((".nexy", ".mdx", ".md", ".py")) and not is_ignored_path(path)


def is_directory_of_pages(path: str) -> bool:
    """True for a path with no extension inside the routes: a folder of pages, not a file."""
    return not Path(path).suffix and is_routes_directory(path)
