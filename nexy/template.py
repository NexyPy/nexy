import os
import threading
from collections.abc import Callable
from typing import Any

from jinja2 import BaseLoader, Environment, TemplateNotFound

from nexy.helpers.fs.vfs import VFS

from .core.config import Config
from .i18n.core import current_locale, trans
from .runtime.markdown import inject_heading_ids as _inject_heading_ids
from .runtime.markdown import render_markdown as _cmark_render_markdown

_ENV_LOCK = threading.Lock()
_SHARED_ENV: Environment | None = None
_LOCALE_INFO = [
    {"code": "fr", "name": "Français", "flag": "🇫🇷"},
    {"code": "en", "name": "English", "flag": "🇬🇧"},
    {"code": "es", "name": "Español", "flag": "🇪🇸"},
    {"code": "pt", "name": "Português", "flag": "🇵🇹"},
    {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
    {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
    {"code": "zh", "name": "中文", "flag": "🇨🇳"},
    {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
    {"code": "ko", "name": "한국어", "flag": "🇰🇷"},
    {"code": "ar", "name": "العربية", "flag": "🇸🇦"},
    {"code": "hi", "name": "हिन्दी", "flag": "🇮🇳"},
]


class NexyTemplateLoader(BaseLoader):
    """Jinja2 loader resolving templates from the VFS first, then the disk."""

    def __init__(self) -> None:
        self.vfs = VFS()

    def get_source(
        self, _environment: Environment, template: str
    ) -> tuple[str, str, Callable[[], bool]]:
        if not self.vfs.exists(template):
            if os.path.exists(template):
                with open(template, encoding="utf-8") as f:
                    return f.read(), template, lambda: True
            raise TemplateNotFound(template)

        source = self.vfs.read(template)
        return source, template, self._is_current(template, source)

    def _is_current(self, template: str, source: str) -> Callable[[], bool]:
        def _uptodate() -> bool:
            try:
                return self.vfs.read(template) == source
            except FileNotFoundError:
                return True

        return _uptodate


def _get_shared_env() -> Environment:
    """Return the module-level shared Jinja2 Environment (thread-safe lazy init)."""
    global _SHARED_ENV
    if _SHARED_ENV is not None:
        return _SHARED_ENV
    with _ENV_LOCK:
        if _SHARED_ENV is not None:
            return _SHARED_ENV
        env = Environment(
            loader=NexyTemplateLoader(),
            auto_reload=True,
            # nosec B701 - Nexy templates are the project's own server-side
            # HTML (see SECURITY.md); autoescape would double-escape
            # hand-written HTML props such as {{ children }}.
        )
        env.globals["trans"] = lambda key, default=None: trans(
            key, default=default, locale=current_locale.get()
        )
        env.globals["_locale_info"] = lambda: {
            "current": current_locale.get(),
            "available": _LOCALE_INFO,
        }
        _SHARED_ENV = env
        return env


class Template:
    """Class to handle Jinja2 and Markdown template rendering."""

    def __init__(self, templates_dir: str = ".") -> None:
        """Initialize the renderer. Reuses a shared Jinja2 Environment for performance.

        Args:
            templates_dir: Base directory exposed to the Jinja2 loader.
        """
        self.config = Config()
        self.templates_dir = templates_dir
        self.env = _get_shared_env()

    def _render_jinja2(self, path: str, context: dict[str, Any]) -> str:
        """Loads and renders a Jinja2 template."""
        template = self.env.get_template(path)
        return template.render(context)

    def invalidate(self, path: str) -> None:
        """Drop a template from the shared cache so the next render recompiles it."""
        if path in self.env.cache:
            del self.env.cache[path]

    def _render_markdown(self, content: str) -> str:
        return _cmark_render_markdown(content)

    def render(self, path: str, context: dict[str, Any] | None = None) -> str:
        """Render a template file, converting Markdown routes to HTML.

        Args:
            path: Template path (VFS-first); `.md`/`.mdx.html` routes are also
                run through the Markdown renderer and heading-id injection.
            context: Jinja2 context passed to the template; defaults to empty.

        Returns:
            The rendered HTML (Markdown-converted for markdown routes, whose
            output also feeds the page table of contents).

        Raises:
            TemplateNotFound: If the path exists neither in the VFS nor on disk.
        """
        if context is None:
            context = {}

        rendered_content = self._render_jinja2(path, context)

        if path.endswith(".md") or path.endswith(".mdx.html"):
            rendered_content = self._render_markdown(rendered_content)
            rendered_content = _inject_heading_ids(rendered_content)
            from nexy.hooks import _toc_storage as _store

            _store.set(rendered_content)

        return rendered_content
