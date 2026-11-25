"""The client build receives the same responsive image manifest as the Python helper."""

from __future__ import annotations

import json
from pathlib import Path

from nexy.modules.frontend import FrontendGenerator
from nexy.modules.images.manifest import IMAGE_MANIFEST, IMAGE_TYPESCRIPT


def test_frontend_generation_publishes_the_image_manifest(nexy_project, tmp_path: Path) -> None:
    nexy_project()
    variant = {"src": "/images/logo.webp", "srcset": "", "sizes": "", "width": 1, "height": 1}
    manifest = {"logo.png": variant}
    (tmp_path / IMAGE_MANIFEST).parent.mkdir(parents=True)
    (tmp_path / IMAGE_MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")

    FrontendGenerator().generate()

    assert '"logo.png"' in (tmp_path / IMAGE_TYPESCRIPT).read_text(encoding="utf-8")
