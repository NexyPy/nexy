import base64
import mimetypes
from collections.abc import Callable
from pathlib import Path

from nexy.core.config import Config
from nexy.image import image
from nexy.modules.images.manifest import load_manifest, normalize_source
from nexy.modules.routers.base_path import public_url


def _data_uri(path: str) -> str:
    """Inline the source bytes when no build variant exists."""
    try:
        file = Path(path)
        if not file.is_absolute():
            file = Path(Config.PROJECT_ROOT).joinpath(path)
        mime, _ = mimetypes.guess_type(str(file))
        encoded = base64.b64encode(file.read_bytes()).decode("ascii")
        return f"data:{mime or 'application/octet-stream'};base64,{encoded}"
    except OSError:
        return ""


class Image:
    @staticmethod
    def create(path: str) -> Callable[..., str]:
        def render(**kwargs: object) -> str:
            """Render `<img>` with attributes, or the URL when used as a value."""
            if kwargs:
                return image(path, **kwargs)  # type: ignore[arg-type]
            variant = load_manifest(Config.PROJECT_ROOT).get(normalize_source(path))
            return public_url(str(variant["src"])) if variant else _data_uri(path)

        return render
