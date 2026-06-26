import ast
import os
import re
from html import escape
from typing import Any

import markdown
from jinja2 import BaseLoader, Environment, TemplateNotFound

from nexy.utils.fs.vfs import VFS

from .compiler.parser.logic import LogicParser
from .compiler.parser.scanner import Scanner
from .compiler.parser.template import TemplateParser
from .core.config import Config
from .core.sandbox import sandboxed_exec
from .i18n.core import L, current_locale, trans
from .runtime.mdx import MdxComponentProcessor
from .runtime.mdxconfig import MdxCompConfig

extension_configs = {
    "pymdownx.highlight": {
        "pygments_lang_class": True,
        "linenums": False,
    }
}

_TOC_HEADING_RE = re.compile(
    r"<h([1-6])(?:\s+[^>]*)?>",
    re.IGNORECASE,
)
_ID_RE = re.compile(r'\s+id="([^"]+)"')
_INNER_TAG_RE = re.compile(r"<[^>]+>")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", slug)


def _inject_heading_ids(html: str) -> str:
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


def _build_toc_html(html: str, depth_range: str = "2-6") -> str:
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

    result.append(f'<li><a href="#{headings[0][1]}" class="toc-link">{escape(headings[0][2])}</a>')

    for level, id_attr, text in headings[1:]:
        if level > prev:
            for _ in range(level - prev):
                result.append("<ul>")
            result.append(f'<li><a href="#{id_attr}" class="toc-link">{escape(text)}</a>')
        elif level < prev:
            for _ in range(prev - level):
                result.append("</li></ul>")
            result.append("</li>")
            result.append(f'<li><a href="#{id_attr}" class="toc-link">{escape(text)}</a>')
        else:
            result.append("</li>")
            result.append(f'<li><a href="#{id_attr}" class="toc-link">{escape(text)}</a>')
        prev = level

    for _ in range(prev - headings[0][0] + 1):
        result.append("</li></ul>")
    result.append("</nav>")
    return "\n".join(result)


class NexyTemplateLoader(BaseLoader):
    def __init__(self) -> None:
        self.vfs = VFS()

    def get_source(self, _environment, template):
        if not self.vfs.exists(template):
            if os.path.exists(template):
                with open(template, encoding="utf-8") as f:
                    return f.read(), template, lambda: True
            raise TemplateNotFound(template)

        source = self.vfs.read(template)
        return source, template, lambda: True


class Template:
    """Class to handle Jinja2 and Markdown template rendering."""

    def __init__(self, templates_dir: str = ".") -> None:
        """Initialize the renderer with Nexy configuration."""
        self.config = Config()
        self.templates_dir = templates_dir

        self.env = Environment(
            loader=NexyTemplateLoader(),
            auto_reload=True,
        )
        self.env.globals["trans"] = lambda key, default=None: trans(
            key, default=default, locale=current_locale.get()
        )
        self.env.globals["_locale_info"] = lambda: {
            "current": current_locale.get(),
            "available": L.available_locales(),
        }

    def _render_jinja2(self, path: str, context: dict[str, Any]) -> str:
        """Loads and renders a Jinja2 template."""
        template = self.env.get_template(path)
        return template.render(context)

    def _render_markdown(self, content: str) -> str:
        return markdown.markdown(
            content, extensions=self.config.MARKDOWN_EXTENSIONS, extension_configs=extension_configs
        )

    def _render_mdx_component(self, path: str, props: dict[str, Any]) -> str:
        source = self._read_source(path)
        scan_result = Scanner().scan(source)

        logic_parser = LogicParser()
        logic_result = logic_parser.process(scan_result.logic_block, current_file=path)

        children = props.get("children", "")

        def slot_fn() -> str:
            return str(children)

        namespace: dict[str, Any] = dict(props)
        namespace["Slot"] = slot_fn

        for p in logic_result.props:
            if p.name not in namespace and p.default:
                try:
                    namespace[p.name] = ast.literal_eval(p.default)
                except (ValueError, SyntaxError):
                    namespace[p.name] = p.default

        if logic_result.python_code:
            sandboxed_exec(logic_result.python_code, namespace)

        parser = TemplateParser()
        jinja_source = parser.parse(scan_result.template_block, known_components=set())
        template = self.env.from_string(jinja_source)
        return template.render(**{k: v for k, v in namespace.items() if k != "Slot"}, Slot=slot_fn)

    def _read_source(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
        loader = self.env.loader
        if hasattr(loader, "vfs") and loader.vfs.exists(path):
            return loader.vfs.read(path)
        return ""

    def render(self, path: str, context: dict[str, Any] | None = None) -> str:
        if context is None:
            context = {}

        rendered_content = self._render_jinja2(path, context)

        if path.endswith(".md"):
            rendered_content = self._render_markdown(rendered_content)
            MdxCompConfig.load()
            if MdxCompConfig.has_mappings():
                processor = MdxComponentProcessor(
                    rendered_content,
                    render_component=self._render_mdx_component,
                )
                rendered_content = processor.process()
            rendered_content = _inject_heading_ids(rendered_content)
            from nexy.hooks import _toc_storage as _store

            _store.set(rendered_content)

        return rendered_content
