"""Pure client-side routing helpers mirroring the generated runtime router.

The authoritative implementation lives in ``vite_entry.py`` as the emitted
``__nexy__/src/runtime.ts``. These helpers exist so the matching semantics can
be unit-tested without a browser; keep both sides in sync.
"""

from typing import Any

NAVIGABLE_EXTS = (".tsx", ".jsx", ".vue", ".svelte", ".solid", ".preact")


def to_segments(pathname: str) -> list[str]:
    """Split a pathname into non-empty segments (mirrors ``toSegments``)."""
    return [part for part in pathname.split("/") if part]


def is_navigable(route: dict[str, Any]) -> bool:
    """Return True when the route file is a client-renderable component."""
    file = route.get("file", "")
    return bool(file) and file.endswith(NAVIGABLE_EXTS)


def match_route(
    routes: list[dict[str, Any]], pathname: str
) -> tuple[dict[str, Any] | None, dict[str, str]]:
    """Return the first navigable route matching *pathname* and its params."""
    parts = to_segments(pathname)
    for route in routes:
        if not is_navigable(route):
            continue
        match = _match_one(route.get("path", ""), parts)
        if match is not None:
            return route, match
    return None, {}


def _match_one(pattern: str, parts: list[str]) -> dict[str, str] | None:
    """Match one route pattern against *parts*, or return None when it differs."""
    segs = to_segments(pattern)
    params: dict[str, str] = {}
    if not _shape_matches(segs, parts):
        return None
    for i, pat in enumerate(segs):
        if pat.startswith("{..."):
            params[pat[4:-1]] = "/".join(parts[i:])
            break
        if pat.startswith("{"):
            params[pat[1:-1]] = parts[i]
            continue
        if pat != parts[i]:
            return None
    return params


def _shape_matches(segs: list[str], parts: list[str]) -> bool:
    """A catch-all tail segment absorbs any number of remaining path parts."""
    if segs and segs[-1].startswith("{..."):
        return len(parts) >= len(segs)
    return len(segs) == len(parts)


def is_external_href(href: str) -> bool:
    """Return True for hrefs the client router must never intercept."""
    return href.startswith(("http", "#", "mailto:"))


def should_intercept_click(
    *,
    href: str | None,
    target: str | None,
    modifier: bool,
    has_route: bool,
) -> bool:
    """Mirror the generated click handler's decision to hijack a link.

    *modifier* is the OR of ctrl/meta/shift/alt; *has_route* is whether the
    href's pathname matches a navigable route.
    """
    if not href or target == "_blank":
        return False
    if modifier or is_external_href(href):
        return False
    return has_route


def should_client_navigate_on_popstate(state: Any) -> bool:
    """Client navigation resumes only for history entries Nexy itself pushed."""
    return bool(state) and bool(isinstance(state, dict) and state.get("nexy"))
