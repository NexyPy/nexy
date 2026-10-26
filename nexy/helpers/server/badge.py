"""The "Built with Nexy" tag: a link in the corner of every HTML page, off with `useBadge`."""

from __future__ import annotations

from starlette.types import ASGIApp

from nexy.helpers.server.html_inject import InjectMiddleware, inject

MARKER = b'id="nexy-badge"'

__all__ = ["MARKER", "BadgeMiddleware", "badge_markup", "inject"]


def badge_markup(version: str) -> bytes:
    """The tag as HTML: its own style, light and dark, no script, no external request."""
    style = (
        "#nexy-badge{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:inline-flex;"
        "align-items:center;gap:8px;padding:10px 16px;border:1px solid #d4d4d4;border-radius:999px;"
        "background:#fff;color:#171717;font:600 14px/1.2 system-ui,sans-serif;text-decoration:none;"
        "box-shadow:0 2px 8px rgba(0,0,0,.1)}"
        "#nexy-badge:hover{border-color:#a3a3a3}"
        "@media(prefers-color-scheme:dark){#nexy-badge{background:#0a0a0a;color:#ededed;"
        "border-color:#303030}#nexy-badge:hover{border-color:#525252}}"
    )
    return (
        f"<style>{style}</style>"
        f'<a id="nexy-badge" href="https://github.com/NexyPy/nexy" target="_blank" '
        f'rel="noopener noreferrer">Built with Nexy {version}</a>'
    ).encode()


class BadgeMiddleware(InjectMiddleware):
    """Adds the tag to HTML responses that have a ``</body>``."""

    def __init__(self, app: ASGIApp, version: str) -> None:
        markup = badge_markup(version)
        super().__init__(app, lambda _scope, _status: markup, MARKER)
