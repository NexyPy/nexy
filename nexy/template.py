import ast
import os
from typing import Any

import markdown
from jinja2 import BaseLoader, Environment, TemplateNotFound

from nexy.utils.fs.vfs import VFS

from .compiler.parser.logic import LogicParser
from .compiler.parser.scanner import Scanner
from .compiler.parser.template import TemplateParser
from .core.config import Config
from .runtime.mdx import MdxComponentProcessor
from .runtime.mdxconfig import MdxCompConfig

extension_configs = {
    "pymdownx.highlight": {
        "pygments_lang_class": True,
        "linenums": False,
    }
}


class NexyVFSLoader(BaseLoader):
    """Jinja2 loader that reads from the VFS."""

    def __init__(self) -> None:
        self.vfs = VFS()

    def get_source(self, environment, template):
        if not self.vfs.exists(template):
            # Fallback to filesystem if not in VFS (e.g. for user templates)
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

        # Security: autoescape prevents XSS
        self.env = Environment(
            loader=NexyVFSLoader(),
            auto_reload=True,
        )

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
            exec(logic_result.python_code, namespace)

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
        return rendered_content
