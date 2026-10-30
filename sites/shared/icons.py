"""The icons both documentation sites draw, as inline SVG that takes the colour of its text."""

from __future__ import annotations

MARK = (
    '<svg viewBox="0 0 20 20" width="14" height="14"><path fill="currentColor" d="M12.5527 0.5459C12.7991 '
    "0.546 13.0362 0.6418 13.2139 0.8125L16.001 3.4902L16.0029 3.4922L19.0605 6.3965C19.2502 6.5766 "
    "19.3574 6.8273 19.3574 7.0889V19.002H13.6377V5.9648H7.2197V0.5459H12.5527ZM6.2197 19.002H0.5V13.5361"
    "L0.5078 13.3906C0.5428 13.0547 0.6978 12.7404 0.9473 12.5078L1.8193 11.6953L6.2197 7.6104V19.002Z"
    '"/></svg>'
)


def _icon(inner: str, extra: str = "") -> str:
    return (
        f'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>'
        f"{inner}</svg>"
    )


def _arrow(path: str, class_name: str) -> str:
    return (
        f'<svg class="{class_name}" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{path}"/></svg>'
    )


ARROW_PREV = _arrow("M19 12H5M12 19l-7-7 7-7", "arrow")
ARROW_NEXT = _arrow("M5 12h14M12 5l7 7-7 7", "arrow")

ICONS = {
    "icon_sidebar": _icon('<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/>'),
    "icon_select": _icon('<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>'),
    "icon_check": _icon('<path d="M20 6 9 17l-5-5"/>'),
    "router_fbr": _icon(
        '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>'
    ),
    "router_modular": _icon(
        '<rect width="7" height="7" x="14" y="3" rx="1"/>'
        '<path d="M10 21V8a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5'
        'a1 1 0 0 0-1-1H3"/>'
    ),
    "router_custom": _icon(
        '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 '
        '7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'
    ),
    "icon_search": _icon('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'),
    "icon_menu": _icon('<path d="M4 6h16M4 12h16M4 18h16"/>'),
    "icon_close": _icon('<path d="M18 6 6 18M6 6l12 12"/>'),
    "icon_sun": _icon(
        '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4'
        'M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/>',
        ' class="sun"',
    ),
    "icon_moon": _icon('<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>', ' class="moon"'),
    "icon_chev": _icon('<path d="m9 18 6-6-6-6"/>', ' class="chev"'),
    "icon_github": _icon(
        '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 '
        "0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 "
        '5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>'
    ),
}
