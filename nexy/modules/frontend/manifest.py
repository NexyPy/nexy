import re
from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.common.json import to_json_literal
from nexy.helpers.fs.path import PathUtil
from nexy.modules.frontend.constants import NAVIGABLE_EXTS
from nexy.modules.frontend.layout_chain import framework_layout_chain


def navigable_entries(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    """Keep only entries the client router can render (framework components)."""
    return [e for e in entries if str(e["file"]).endswith(NAVIGABLE_EXTS)]


def collect_route_names() -> tuple[set[str], set[str]]:
    """(layout names, special names) recognized by the router, lowercased."""
    active_exts = set(Config.ROUTE_FILE_EXTENSIONS)
    layout_names = {n.lower() for n in Config.LAYOUT_FILE_NAMES}
    layout_names |= {"layout" + e.lower() for e in active_exts}
    special_names = {
        n.lower()
        for n in [
            *Config.NOTFOUND_FILE_NAMES,
            *Config.ERROR_FILE_NAMES,
            *Config.LOADING_FILE_NAMES,
        ]
    }
    special_names |= {"notfound" + e.lower() for e in active_exts}
    special_names |= {"errors" + e.lower() for e in active_exts}
    special_names |= {"loading" + e.lower() for e in active_exts}
    return layout_names, special_names


def file_to_url(path: Path, routes_root: Path) -> str:
    rel = path.relative_to(routes_root).as_posix()
    stem = rel.rsplit(".", 1)[0]
    if stem.endswith("/index") or stem == "index":
        stem = stem[: -len("/index")] if len(stem) > len("/index") else ""
    url = "/" + stem
    url = re.sub(r"\[\.\.\.([^\]]+)\]", r"{...\1}", url)
    url = re.sub(r"\[([^\]]+)\]", r"{\1}", url)
    url = re.sub(r"\(([^)]+)\)", "", url)
    url = re.sub(r"/+", "/", url)
    return url if url != "/" else "/"


def extract_params(url: str) -> list[str]:
    return re.findall(r"\{([^}]+)\}", url)


def sort_key(url: str) -> tuple[int, int]:
    if ":path" in url or "{...}" in url:
        return 2, 0
    if "{" in url:
        literals = sum(1 for seg in url.split("/") if seg and not seg.startswith("{"))
        return 1, -literals
    return 0, 0


class RouteManifestBuilder:
    """Builds the route tree and renders routes.auto.ts / routes.client.auto.ts.

    Each entry records the URL path, the component file, its layout chain
    and its dynamic params. The client router walks the same tree the
    server uses, so navigation never duplicates routing logic.
    """

    def __init__(self) -> None:
        self._layout_cache: dict[str, str | None] = {}

    def entries(self) -> list[dict[str, object]]:
        """Collect route entries from src/routes (URL path, file, layout, params)."""
        routes_root = Path("src/routes")
        if not routes_root.is_dir():
            return []
        layout_names, special_names = collect_route_names()

        entries: list[dict[str, object]] = []
        for path in sorted(routes_root.rglob("*")):
            if not path.is_file() or path.suffix not in set(Config.ROUTE_FILE_EXTENSIONS):
                continue
            name = path.name.lower()
            if name in layout_names or name in special_names:
                continue
            rel = path.relative_to(routes_root).as_posix()
            if any(part.startswith("_") or part.startswith(".") for part in rel.split("/")):
                continue
            url = file_to_url(path, routes_root)
            layout = self._closest_layout(path, routes_root, layout_names)
            entries.append(
                {
                    "path": url,
                    "file": f"/src/routes/{rel}",
                    "layout": layout,
                    "layouts": framework_layout_chain(path, routes_root),
                    "params": extract_params(url),
                }
            )
        entries.sort(key=lambda e: sort_key(str(e["path"])))
        return entries

    def render_full(self) -> str | None:
        """Render routes.auto.ts (full tree with the Route type union)."""
        entries = self.entries()
        if not entries and not Path("src/routes").is_dir():
            return None
        return self._render(entries, include_route_type=True)

    def render_client(self) -> str | None:
        """Render routes.client.auto.ts (navigable components only)."""
        entries = navigable_entries(self.entries())
        if not entries and not Path("src/routes").is_dir():
            return None
        return self._render(entries, include_route_type=False)

    def write(self, dest_dir: Path) -> None:
        """Write full and client manifests under *dest_dir* when they changed."""
        dest_dir.mkdir(parents=True, exist_ok=True)
        entries = self.entries()
        if not entries and not Path("src/routes").is_dir():
            return
        PathUtil.write_if_changed(dest_dir / "routes.auto.ts", self._render(entries, True))
        client = self._render(navigable_entries(entries), include_route_type=False)
        PathUtil.write_if_changed(dest_dir / "routes.client.auto.ts", client)

    def _render(self, entries: list[dict[str, object]], include_route_type: bool) -> str:
        """Render routes.auto.ts (full) or routes.client.auto.ts (navigable-only)."""
        lines = [
            "export type NexyRoute = {",
            "  path: string;",
            "  file: string;",
            "  layout: string | null;",
            "  layouts: string[];",
            "  params: string[];",
            "};",
            "",
        ]
        lines.append("export const NEXY_ROUTES: NexyRoute[] = [")
        for e in entries:
            lines.append(
                "  { path: "
                + to_json_literal(e["path"])
                + ", file: "
                + to_json_literal(e["file"])
                + ", layout: "
                + to_json_literal(e["layout"])
                + ", layouts: "
                + to_json_literal(e.get("layouts", []))
                + ", params: "
                + to_json_literal(e["params"])
                + " },"
            )
        lines.append("];")
        if include_route_type:
            lines.append("")
            route_parts: list[str] = []
            seen: set[str] = set()
            for e in entries:
                url = str(e["path"])
                if url in seen:
                    continue
                seen.add(url)
                if "{" in url:
                    literal = re.sub(r"\{[^}]+:path\}", "${string}", url)
                    literal = re.sub(r"\{[^}]+\}", "${string}", literal)
                    route_parts.append(f"`{literal}`")
                else:
                    route_parts.append(to_json_literal(url))
            if route_parts:
                lines.append("export type Route = " + " | ".join(route_parts) + ";")
        return "\n".join(lines) + "\n"

    def _closest_layout(self, path: Path, routes_root: Path, layout_names: set[str]) -> str | None:
        start = path.parent.as_posix()
        if start in self._layout_cache:
            return self._layout_cache[start]
        current = path.parent
        while True:
            for name in layout_names:
                candidate = current / name
                if candidate.is_file():
                    rel = candidate.relative_to(routes_root).as_posix()
                    self._layout_cache[start] = f"/src/routes/{rel}"
                    return self._layout_cache[start]
            if current == routes_root or current == current.parent:
                self._layout_cache[start] = None
                return None
            current = current.parent
