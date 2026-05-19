import os
from typing import Any

from nexy.utils.fs.vfs import VFS

from .core.config import Config

class NexyVFSLoader:
    """Jinja2 loader that reads from the VFS."""

    def __init__(self) -> None:
        self.vfs = VFS()

    def get_source(self, environment, template):
        from jinja2 import TemplateNotFound

        if not self.vfs.exists(template):
            if os.path.exists(template):
                with open(template, encoding="utf-8") as f:
                    return f.read(), template, lambda: True
            raise TemplateNotFound(template)

        source = self.vfs.read(template)
        return source, template, lambda: True

    def load(self, environment, name, globals=None):
        source, filename, uptodate = self.get_source(environment, name)
        if globals is None:
            globals = {}
        bcc = environment.bytecode_cache
        if bcc is not None:
            bucket = bcc.get_bucket(environment, name, filename, source)
            code = bucket.code
        else:
            code = None
        if code is None:
            code = environment.compile(source, name, filename)
        if bcc is not None and bucket.code is None:
            bucket.code = code
            bcc.set_bucket(bucket)
        return environment.template_class.from_code(environment, code, globals, uptodate)


class Template:
    """Class to handle Jinja2 and Markdown template rendering."""

    def __init__(self, templates_dir: str = ".") -> None:
        from jinja2 import Environment

        self.config = Config()
        self.templates_dir = templates_dir

        self.env = Environment(
            loader=NexyVFSLoader(),
            auto_reload=True,
        )

    def _render_jinja2(self, path: str, context: dict[str, Any]) -> str:
        template = self.env.get_template(path)
        return template.render(context)

    def _render_markdown(self, content: str) -> str:
        import markdown as _markdown

        extension_configs = {
            "pymdownx.highlight": {
                "pygments_lang_class": True,
                "linenums": False,
            }
        }
        return _markdown.markdown(
            content, extensions=self.config.MARKDOWN_EXTENSIONS, extension_configs=extension_configs
        )

    def render(self, path: str, context: dict[str, Any] | None = None) -> str:
        import traceback

        if context is None:
            context = {}

        try:
            rendered_content = self._render_jinja2(path, context)

            if path.endswith(".md"):
                return self._render_markdown(rendered_content)
            return rendered_content
        except Exception:
            traceback.print_exc()
            raise
