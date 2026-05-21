import ast
import html as html_mod
import json
import re
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from jinja2 import Environment

from nexy.compiler.parser.logic import LogicParser
from nexy.compiler.parser.scanner import Scanner
from nexy.compiler.parser.template import TemplateParser
from nexy.core.config import Config
from nexy.runtime.mdxconfig import MdxCompConfig, MdxComponentMapping

_VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)

_LANG_RE = re.compile(r"\blanguage-(\w+)\b")


def _project_root() -> Path:
    return Path(Config.PROJECT_ROOT or ".").resolve()


class _MdxReplacer(HTMLParser):
    def __init__(
        self,
        config: type[MdxCompConfig],
        render_nexy: Callable[[str, dict[str, Any]], str],
    ) -> None:
        super().__init__(convert_charrefs=False)
        self.config = config
        self.render_nexy = render_nexy
        self.output: list[str] = []
        self._depth = 0
        self._mapping: MdxComponentMapping | None = None
        self._attrs: dict[str, str] = {}
        self._parts: list[str] = []
        self._pending_language: str | None = None

    def _tag_text(self) -> str:
        text = self.get_starttag_text()
        return text or ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        tag_text = self._tag_text()

        if tag == "div":
            lang_match = _LANG_RE.search(attrs_dict.get("class", ""))
            if lang_match:
                self._pending_language = lang_match.group(1)

        if self._depth > 0:
            self._depth += 1
            self._parts.append(tag_text)
            return

        mapping = self.config.get_mapping(tag)
        if mapping:
            self._depth = 1
            self._mapping = mapping
            self._attrs = attrs_dict
            self._parts = [tag_text]

            if tag in _VOID_ELEMENTS:
                self._emit_replacement()
                self._depth = 0
            return

        self.output.append(tag_text)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div":
            self._pending_language = None

        if self._depth > 0:
            self._depth -= 1
            self._parts.append(f"</{tag}>")
            if self._depth == 0:
                self._emit_replacement()
            return

        self.output.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._depth > 0:
            self._parts.append(data)
            return
        self.output.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._depth > 0:
            self._parts.append(f"&{name};")
            return
        self.output.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._depth > 0:
            self._parts.append(f"&#{name};")
            return
        self.output.append(f"&#{name};")

    @staticmethod
    def _extract_code_attrs(raw: str) -> dict[str, str]:
        code_match = re.search(r"<code(\s[^>]*?)?>", raw, re.DOTALL)
        if not code_match or not code_match.group(1):
            return {}
        attrs: dict[str, str] = {}
        for name, value in re.findall(r'(\w+)\s*=\s*"([^"]*?)"', code_match.group(1)):
            attrs[name] = value
        return attrs

    def _emit_replacement(self) -> None:
        mapping = self._mapping
        assert mapping is not None
        attrs = self._attrs
        raw = "".join(self._parts)

        element = mapping.element
        props: dict[str, str] = dict(attrs)

        if element == "pre":
            props["children"] = raw
        else:
            props["children"] = self._extract_children(raw, element)

        if element == "pre":
            lang_match = _LANG_RE.search(attrs.get("class", ""))
            if lang_match:
                props["language"] = lang_match.group(1)
            code_attrs = self._extract_code_attrs(raw)
            for k, v in code_attrs.items():
                if k not in props and k != "class":
                    props[k] = v
            if "language" not in props:
                code_lang = _LANG_RE.search(code_attrs.get("class", ""))
                if code_lang:
                    props["language"] = code_lang.group(1)

            if "language" not in props and self._pending_language:
                props["language"] = self._pending_language

        root = _project_root()
        resolved = MdxCompConfig.resolve_source(mapping.source, root)

        if resolved and resolved.suffix.lower() == ".nexy":
            replacement = self.render_nexy(str(resolved), props)
        else:
            rel = str(resolved.relative_to(root)).replace("\\", "/") if resolved else mapping.source
            ext = resolved.suffix.lower() if resolved else ""
            fw = Config.FRONTEND_EXTENSIONS.get(ext)
            replacement = _emit_ncc(mapping.symbol, rel, fw, props)

        self.output.append(replacement)

        self._mapping = None
        self._attrs = {}
        self._parts = []

    @staticmethod
    def _extract_children(raw: str, element: str) -> str:
        first_gt = raw.index(">") + 1
        end_tag = f"</{element}>"
        return raw[first_gt : -len(end_tag)]


def _emit_ncc(symbol: str, source_rel: str, framework: str | None, props: dict[str, Any]) -> str:
    safe_props: dict[str, str] = {}
    for k, v in props.items():
        if isinstance(v, (str, int, float, bool)):
            safe_props[k] = str(v)
    props_json = json.dumps(safe_props, ensure_ascii=True).replace("'", "&#39;")

    fallback = html_mod.escape(props.get("children", ""))
    return (
        f"<ncc "
        f'data-nexy-fw="{framework or ""}" '
        f'data-nexy-path="{source_rel}" '
        f'data-nexy-symbol="{symbol}" '
        f"data-nexy-props='{props_json}' "
        f'style="display:contents">'
        f"{fallback}"
        f"</ncc>"
    )


class MdxComponentProcessor:
    def __init__(
        self,
        html: str,
        render_component: Callable[[str, dict[str, Any]], str] | None = None,
    ) -> None:
        self.html = html
        self.render_component = render_component or _render_nexy_template

    def process(self) -> str:
        if not MdxCompConfig.has_mappings():
            return self.html

        parser = _MdxReplacer(MdxCompConfig, self.render_component)
        parser.feed(self.html)
        parser.close()
        return "".join(parser.output)


def _render_nexy_template(source_path: str, props: dict[str, Any]) -> str:
    source = Path(source_path).read_text(encoding="utf-8")
    scan_result = Scanner().scan(source)

    logic_parser = LogicParser()
    logic_result = logic_parser.process(scan_result.logic_block, current_file=source_path)

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
    env = Environment()
    template = env.from_string(jinja_source)
    return str(template.render(**{k: v for k, v in namespace.items() if k != "Slot"}, Slot=slot_fn))
