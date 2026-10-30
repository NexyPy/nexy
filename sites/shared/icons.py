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
    "area_nexy": _icon('<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>'),
    "area_fbr": _icon(
        '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>'
    ),
    "area_modular": _icon('<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>'),
    "area_cli": _icon('<path d="m5 8 5 4-5 4M13 17h6"/>'),
    "area_core": _icon(
        '<rect width="14" height="14" x="5" y="5" rx="2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>'
    ),
    "area_custom": _icon(
        '<path d="M8 2h8a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm0 2v3h8V4H8zm0 5v10h8V9H8z"/>'
    ),
    "icon_search": _icon('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'),
    "icon_menu": _icon('<path d="M4 6h16M4 12h16M4 18h16"/>'),
    "icon_close": _icon('<path d="M18 6 6 18M6 6l12 12"/>'),
    "icon_book": _icon("M5 12h14M12 5l7 7-7 7", ' class="arrow"'),
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
