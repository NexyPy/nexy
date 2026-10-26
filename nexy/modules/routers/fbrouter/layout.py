"""Finding the layout that wraps a route: the closest `layout.*` file above it."""

from __future__ import annotations

from pathlib import Path

from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.helpers.fs.ancestors import walk_up


def _layout_names(nexy_only: bool) -> list[str]:
    return [name for name in Config.LAYOUT_FILE_NAMES if not nexy_only or name.endswith(".nexy")]


def _module_of(layout_file: Path) -> str:
    """The dotted module of a compiled layout, under the compiled namespace."""
    try:
        relative = layout_file.relative_to(Path.cwd()).as_posix()
    except ValueError:
        relative = layout_file.as_posix()
    mapped = StringTransform.normalize_route_path_for_namespace(relative)
    namespace = Config.NAMESPACE.replace("/", ".")
    prefix = namespace if namespace.endswith(".") else f"{namespace}."
    return prefix + mapped.rsplit(".", 1)[0].replace("/", ".")


class RouteLayout:
    @staticmethod
    def get_closest_import(
        source_path: str, is_layout: bool = False, nexy_only: bool = False
    ) -> str | None:
        """The module of the nearest layout above *source_path* (above its folder, for a layout)."""
        try:
            path = Path(source_path).resolve()
            start = path.parent.parent if is_layout else path.parent
            names = _layout_names(nexy_only)
            for directory in walk_up(start, Path(Config.ROUTER_PATH).resolve().parent):
                found = next(
                    (c for c in (directory / n for n in names) if c.is_file() and c != path), None
                )
                if found:
                    return _module_of(found)
        except Exception:
            return None
        return None
