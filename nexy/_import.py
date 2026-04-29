import hashlib
import json
import base64
import mimetypes
from pathlib import Path
from html import escape as _html_escape
from typing import Any, Callable, Dict
from nexy.core.config import Config
from pathlib import Path as _Path


class Import:
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.path = path
        self.framework = framework.lower()
        self.symbol = symbol
        self._seq = 0

    def __call__(self, **kwargs: Any) -> str:
        self._seq += 1
        mount_id = self._mount_id(self.path, self.symbol, self._seq)
        props = self._serialize_props(kwargs)
        return self._placeholder(self.framework, self.path, mount_id, props)

    def _mount_id(self, path: str, symbol: str, seq: int) -> str:
        base = f"{path}|{symbol}|{seq}"
        h = hashlib.md5(base.encode()).hexdigest()[:10]
        return f"nexy-{h}"

    def _serialize_props(self, props: Dict[str, Any]) -> str:
        try:
            return json.dumps(props)
        except Exception:
            return "{}"

    def _placeholder(self, framework: str, path: str, mount_id: str, props_json: str) -> str:
        aliases = getattr(Config, "ALIASES", {}) or {}
        resolved = path
        for key, target in aliases.items():
            k = key.rstrip("/")
            if resolved == k or resolved.startswith(f"{k}/"):
                t = target.lstrip("/")
                suffix = resolved[len(k):].lstrip("/")
                resolved = f"/{t}/{suffix}" if suffix else f"/{t}"
                break
        if not resolved.startswith("/"):
            if resolved.startswith("./") or resolved.startswith("../") or not any(resolved.startswith(prefix) for prefix in aliases.keys()):
                stripped = resolved
                while stripped.startswith("./"):
                    stripped = stripped[2:]
                while stripped.startswith("../"):
                    stripped = stripped[3:]
                candidates = ["src", "src/components"]
                for base in candidates:
                    from pathlib import Path as _P
                    candidate_path = _P(getattr(Config, "PROJECT_ROOT", ".")).joinpath(base, stripped)
                    if candidate_path.is_file():
                        resolved = f"/{candidate_path.as_posix().lstrip('/')}"
                        break
        url = resolved if resolved.startswith("/") else f"/{resolved}"
        esc_props = _html_escape(props_json, quote=True)
        esc_symbol = _html_escape(self.symbol, quote=True)
        esc_fw = _html_escape(framework, quote=True)
        esc_url = _html_escape(url, quote=True)

        prod_marker = _Path("__nexy__/nexy.prod").is_file()
        if framework == "vue" or framework == "svelte":
            default = _Path(f"__nexy__/client/static{esc_url}.html")
        else:
            default = _Path(f"__nexy__/client/static{esc_url.replace('.tsx','')}.Default.html")
        export = _Path(f"__nexy__/client/static{esc_url.replace('.tsx','')}.{esc_symbol}.html")

        if export.is_file():
            content = export.read_text(encoding="utf-8")
        elif default.is_file():
            content = default.read_text(encoding="utf-8")
        else:
            content = ""

        if prod_marker:
            key_src = url
            h = hashlib.md5(key_src.encode("utf-8")).hexdigest()
            return (
                f'<ncc id="{mount_id}" '
                f'data-nexy-fw="{esc_fw}" '
                f'data-nexy-key="{h}" '
                f'style="display: contents;"'
                f'data-nexy-symbol="{esc_symbol}" '
                f'data-nexy-props="{esc_props}">{content}</ncc>'
            )
        else:
            key_src = url
            h = hashlib.md5(key_src.encode("utf-8")).hexdigest()

            return (
                f'<ncc id="{mount_id}" '
                f'data-nexy-fw="{esc_fw}" '
                f'data-nexy-path="{esc_url}" '
                f'data-nexy-key="{h}" '
                f'style="display: contents;"'
                f'data-nexy-symbol="{esc_symbol}" '
                f'data-nexy-props="{esc_props}">{content}</ncc>'
            )


def __Import(path: str, framework: str, symbol: str) -> Callable[..., Any]:
    ext = Path(path).suffix.lower()

    if ext == ".json":
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(Config.PROJECT_ROOT).joinpath(path)
            with p.open("r", encoding="utf-8") as f:
                result: Any = json.load(f)
                return lambda: result
        except Exception:
            return lambda: {}

    if ext == ".css":
        return lambda: ""

    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(Config.PROJECT_ROOT).joinpath(path)
            data = p.read_bytes()
            mime, _ = mimetypes.guess_type(str(p))
            if not mime:
                mime = "application/octet-stream"
            b64 = base64.b64encode(data).decode("ascii")
            return lambda: f"data:{mime};base64,{b64}"
        except Exception:
            return lambda: ""

    return Import(path=path, framework=framework, symbol=symbol)
