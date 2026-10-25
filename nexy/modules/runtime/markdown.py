import re
from html import escape

import cmarkgfm  # type: ignore[import-untyped]

from nexy.core.config import Config

_TOC_HEADING_RE = re.compile(
    r"<h([1-6])(?:\s+[^>]*)?>",
    re.IGNORECASE,
)
_ID_RE = re.compile(r'\s+id="([^"]+)"')
_INNER_TAG_RE = re.compile(r"<[^>]+>")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", slug)


def render_markdown(content: str) -> str:
    """Render a markdown string to HTML using cmarkgfm (GFM)."""
    options = getattr(Config, "MARKDOWN_OPTIONS", 0)
    html = cmarkgfm.github_flavored_markdown_to_html(content, options)
    return str(html)


def inject_heading_ids(html: str) -> str:
    """Ensure every heading in HTML has an id attribute, adding slugs as needed."""
    result: list[str] = []
    pos = 0
    while pos < len(html):
        m = _TOC_HEADING_RE.search(html, pos)
        if not m:
            result.append(html[pos:])
            break
        level = int(m.group(1))
        tag_start = m.start()
        tag_end = m.end()
        result.append(html[pos:tag_start])

        tag_text = html[tag_start:tag_end]
        if _ID_RE.search(tag_text):
            result.append(tag_text)
        else:
            closing = f"</h{level}>"
            close_pos = html.find(closing, tag_end)
            if close_pos == -1:
                result.append(tag_text)
                pos = tag_end
                continue
            inner = html[tag_end:close_pos]
            text = _INNER_TAG_RE.sub("", inner).strip()
            if text:
                slug = _slugify(text)
                result.append(tag_text[:-1] + f' id="{slug}">')
            else:
                result.append(tag_text)
        pos = tag_end
    return "".join(result)


def build_toc_html(html: str, depth_range: str = "2-6") -> str:
    """Extract headings from rendered HTML and build a hierarchical TOC."""
    try:
        parts = depth_range.split("-")
        min_level = int(parts[0])
        max_level = int(parts[1]) if len(parts) > 1 else int(parts[0])
    except (ValueError, IndexError):
        min_level, max_level = 2, 6

    headings: list[tuple[int, str, str]] = []
    pos = 0
    while pos < len(html):
        m = _TOC_HEADING_RE.search(html, pos)
        if not m:
            break
        level = int(m.group(1))
        tag_start = m.start()
        tag_end = m.end()
        closing = f"</h{level}>"
        close_pos = html.find(closing, tag_end)
        if close_pos == -1:
            pos = tag_end
            continue

        if level < min_level or level > max_level:
            pos = close_pos + len(closing)
            continue

        tag_text = html[tag_start:tag_end]
        id_m = _ID_RE.search(tag_text)
        id_attr = id_m.group(1) if id_m else ""

        inner = html[tag_end:close_pos]
        text = _INNER_TAG_RE.sub("", inner).strip()
        if not text:
            pos = close_pos + len(closing)
            continue

        if not id_attr:
            id_attr = _slugify(text)

        headings.append((level, id_attr, text))
        pos = close_pos + len(closing)

    if not headings:
        return ""

    result: list[str] = ['<nav class="toc"><ul>']
    prev = headings[0][0]

    first_id = escape(headings[0][1], quote=True)
    result.append(f'<li><a href="#{first_id}" class="toc-link">{escape(headings[0][2])}</a>')

    for level, id_attr, text in headings[1:]:
        if level > prev:
            for _ in range(level - prev):
                result.append("<ul>")
            result.append(
                f'<li><a href="#{escape(id_attr, quote=True)}" class="toc-link">{escape(text)}</a>'
            )
        elif level < prev:
            for _ in range(prev - level):
                result.append("</li></ul>")
            result.append("</li>")
            result.append(
                f'<li><a href="#{escape(id_attr, quote=True)}" class="toc-link">{escape(text)}</a>'
            )
        else:
            result.append("</li>")
            result.append(
                f'<li><a href="#{escape(id_attr, quote=True)}" class="toc-link">{escape(text)}</a>'
            )
        prev = level

    for _ in range(prev - headings[0][0] + 1):
        result.append("</li></ul>")
    result.append("</nav>")
    return "\n".join(result)


__all__ = [
    "render_markdown",
    "inject_heading_ids",
    "build_toc_html",
    "_slugify",
]
