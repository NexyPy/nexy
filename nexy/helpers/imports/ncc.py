import hashlib
import json
from collections.abc import Callable
from html import escape as _html_escape
from pathlib import Path
from typing import Any

from nexy.core.config import Config


def _escape(value: str) -> str:
    return _html_escape(value, quote=True)


def _expand_alias(path: str) -> str:
    """*path* with a configured alias (``@/ui``) replaced by what it stands for."""
    for key, target in (Config.ALIASES or {}).items():
        alias = key.rstrip("/")
        if path == alias or path.startswith(f"{alias}/"):
            suffix = path[len(alias) :].lstrip("/")
            base = target.lstrip("/")
            return f"/{base}/{suffix}" if suffix else f"/{base}"
    return path


def _island_attributes(directive: str | None, media: str | None) -> str:
    """The attributes of an island that hydrates later (``client:idle``, ``client:media``...)."""
    if not directive:
        return ""
    attributes = f'data-nexy-island="" data-nexy-directive="{_html_escape(directive, quote=True)}" '
    if media and directive == "client:media":
        attributes += f'data-nexy-media="{_html_escape(media, quote=True)}" '
    return attributes


class NexyClientComponent:
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.path = path
        self.framework = framework.lower()
        self.symbol = symbol
        self._seq = 0

    def generate(self, props: dict[str, Any], caller: Callable[[], Any] | None = None) -> str:
        self._seq += 1
        mount_id = self._generate_mount_id()
        if caller:
            props["children"] = f"{caller()}"
        directive = props.pop("directive", None)
        media = props.pop("media", None)
        props_json = self._serialize_props(props)
        url = self._resolve_path()

        return self._render_tag(url, mount_id, props_json, directive, media)

    def _generate_mount_id(self) -> str:
        base = f"{self.path}|{self.symbol}|{self._seq}"
        h = hashlib.md5(base.encode(), usedforsecurity=False).hexdigest()[:10]
        return f"nexy-{h}"

    def _serialize_props(self, props: dict[str, Any]) -> str:
        try:
            return json.dumps(props)
        except Exception:
            return "{}"

    def _resolve_path(self) -> str:
        resolved = _expand_alias(self.path)
        if not resolved.startswith(("/", "./", "../")):
            stripped = resolved.lstrip("./")
            for base in ("src", "src/components"):
                candidate = Path(Config.PROJECT_ROOT).joinpath(base, stripped)
                if candidate.is_file():
                    return f"/{candidate.as_posix().lstrip('/')}"
        return resolved if resolved.startswith("/") else f"/{resolved}"

    def _render_tag(
        self,
        url: str,
        mount_id: str,
        props_json: str,
        directive: str | None = None,
        media: str | None = None,
    ) -> str:
        escape = _escape
        in_production = Path("__nexy__/nexy.prod").is_file()
        key_hash = hashlib.md5(url.encode("utf-8"), usedforsecurity=False).hexdigest()
        attributes = [
            f'id="{mount_id}"',
            f'data-nexy-fw="{escape(self.framework)}"',
            "" if in_production else f'data-nexy-path="{escape(url)}"',
            f'data-nexy-key="{key_hash}"',
            'style="display: contents;"',
            _island_attributes(directive, media).strip(),
            f'data-nexy-symbol="{escape(self.symbol)}"',
            f'data-nexy-props="{escape(props_json)}"',
        ]
        content = self._get_static_content(escape(url), escape(self.symbol))
        return f"<ncc {' '.join(filter(None, attributes))}>{content}</ncc>"

    def _get_static_content(self, url: str, symbol: str) -> str:
        clean_url = url.replace(".tsx", "")
        if self.framework in ["vue", "svelte"]:
            default_path = Path(f"__nexy__/client/static{url}.html")
        else:
            default_path = Path(f"__nexy__/client/static{clean_url}.Default.html")

        export_path = Path(f"__nexy__/client/static{clean_url}.{symbol}.html")

        if export_path.is_file():
            return export_path.read_text(encoding="utf-8")
        if default_path.is_file():
            return default_path.read_text(encoding="utf-8")
        return ""
