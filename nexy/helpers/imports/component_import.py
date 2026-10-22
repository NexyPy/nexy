from collections.abc import Callable
from pathlib import Path
from typing import Any

from nexy.helpers.common.json import Json
from nexy.helpers.imports.css import CSS
from nexy.helpers.imports.images import Image
from nexy.helpers.imports.ncc import NexyClientComponent


class Import:
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.generator = NexyClientComponent(path, framework, symbol)

    def __call__(self, **kwargs: Any) -> str:
        return self.generator.generate(kwargs)


def _Import(path: str, framework: str, symbol: str) -> Callable[..., Any]:
    ext = Path(path).suffix.lower()

    if ext == ".json":
        return Json.create(path)

    if ext == ".css":
        return CSS.create(path)

    if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        return Image.create(path)

    return Import(path, framework, symbol)
