"""Frontend generation: route manifests, client entry and build assets."""

from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.fs.path import PathUtil
from nexy.modules.frontend.assets import copy_ssg_scripts, copy_vite_config, write_aliases
from nexy.modules.frontend.frameworks import preact, react, solid, svelte, vue
from nexy.modules.frontend.manifest import RouteManifestBuilder
from nexy.modules.frontend.vite_entry import generate_vite_entry
from nexy.modules.images.manifest import load_manifest, write_image_typescript

_NOCHECK = "// @ts-nocheck\n"


def _exempt_generated_typescript() -> None:
    """Generated files are not user source, so the project's strict tsc skips them."""
    for path in Path("__nexy__").rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        content = path.read_text(encoding="utf-8")
        if content.startswith(_NOCHECK):
            continue
        PathUtil.write_if_changed(path, _NOCHECK + content)


class FrontendGenerator:
    """Orchestrates route manifests, the client entry and build assets."""

    def __init__(self) -> None:
        self.config = Config()
        self._manifest = RouteManifestBuilder()

    def generate(self, ssg: bool = False) -> None:
        self._write_route_manifest()
        generate_vite_entry(self.config.useFF)
        write_image_typescript(load_manifest())
        copy_vite_config()
        write_aliases()
        if ssg:
            copy_ssg_scripts(list(self.config.excludeDirs or []))
        _exempt_generated_typescript()

    def generate_route_manifest(self) -> str | None:
        """Build the shared route tree (routes.auto.ts contract) from src/routes.

        Each entry records the URL path, the component file, its layout chain
        and its dynamic params. The client router walks the same tree the
        server uses, so navigation never duplicates routing logic.
        """
        return self._manifest.render_full()

    def generate_client_route_manifest(self) -> str | None:
        """Build the client-only manifest (navigable framework components)."""
        return self._manifest.render_client()

    def _write_route_manifest(self) -> None:
        self._manifest.write(Path("__nexy__") / "src")


__all__ = [
    "preact",
    "react",
    "svelte",
    "vue",
    "solid",
]
