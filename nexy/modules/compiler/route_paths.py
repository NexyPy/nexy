"""Where a route file's compiled module goes, what its component is called, where it is served."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform


@dataclass(frozen=True)
class RoutePaths:
    """The generated files of one route source and its URL."""

    source: str
    namespaced: str
    py_path: str
    html_path: str
    component: str
    pathname: str

    @property
    def meta_path(self) -> str:
        return Path(self.namespaced).with_suffix(".meta.json").as_posix()

    @property
    def package(self) -> str:
        """The folder of the generated module, whose ancestors must be Python packages."""
        return Path(self.namespaced).parent.as_posix()


def route_paths(source: str, stem: str) -> RoutePaths:
    """Derive the generated module paths, component name and URL pathname of *source*."""
    names = StringTransform()
    namespaced = f"{Config.NAMESPACE}{names.normalize_route_path_for_namespace(source)}"
    router = Path(Config.ROUTER_PATH).as_posix()
    cleaned = source.replace(f"{Config.NAMESPACE}{router}", "").replace(router, "").split(".")[0]
    return RoutePaths(
        source=source,
        namespaced=namespaced,
        py_path=Path(namespaced).with_suffix(".py").as_posix(),
        html_path=Path(namespaced).with_suffix(".html").as_posix(),
        component=names.get_component_name(stem) or "Index",
        pathname=Pathname(cleaned).process(),
    )
