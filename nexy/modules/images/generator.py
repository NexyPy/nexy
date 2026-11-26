"""Turn local images into hashed WebP variants during `nx build`."""

from __future__ import annotations

import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexy.core.config import Config
from nexy.modules.images.manifest import Variant, normalize_source

DEFAULT_WIDTHS = (320, 640, 960, 1280)
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
TEXT_EXTS = {".nexy", ".md", ".mdx", ".ts", ".tsx", ".jsx", ".vue", ".svelte"}
REFERENCE = re.compile(r"""["']([^"']+\.(?:png|jpe?g|webp|gif|bmp))["']""", re.IGNORECASE)


class ImageBuildError(ValueError):
    """A local image cannot be turned into variants."""


@dataclass(frozen=True)
class ImageBuild:
    manifest: dict[str, Variant]
    files: dict[str, bytes]


def _pillow() -> Any:
    """Pillow is optional: a project without it keeps the plain URL fallback."""
    try:
        from PIL import Image as PillowImage
    except ImportError:
        return None
    return PillowImage


def validate_widths(widths: list[int], source: str) -> None:
    """A width must be a positive integer, or the build names the offending image."""
    for width in widths:
        if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
            raise ImageBuildError(f"{source}: invalid width {width!r} (width must be positive)")


def _display(root: Path, path: Path) -> str:
    """The project-relative name used in build errors."""
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_reference(root: Path, file: Path, reference: str) -> Path | None:
    """Where an image path in a source file points, before any build has run."""
    ref = reference.replace("\\", "/").split("?")[0].split("#")[0]
    if ref.startswith(("http://", "https://", "data:", "//")):
        return None
    if ref.startswith("/"):
        candidates = [root / "public" / ref.lstrip("/"), root / ref.lstrip("/")]
    elif ref.startswith(("./", "../")):
        candidates = [file.parent / ref]
    else:
        candidates = [file.parent / ref, root / ref, root / "public" / ref]
    return candidates[0]


def find_sources(root: Path) -> list[Path]:
    """Images under src/ and public/, plus every local image a source file names."""
    found: set[Path] = set()
    public = root / "public"
    src = root / "src"
    for directory in (public, src):
        if directory.is_dir():
            found.update(
                path.resolve()
                for path in directory.rglob("*")
                if path.is_file() and path.suffix.lower() in IMAGE_EXTS
            )
    if src.is_dir():
        for path in src.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_EXTS:
                _add_references(root, path, found)
    return sorted(found, key=lambda path: path.as_posix())


def _add_references(root: Path, file: Path, found: set[Path]) -> None:
    """Read one source file and add the local images it names."""
    try:
        text = file.read_text(encoding="utf-8")
    except OSError:
        return
    for reference in REFERENCE.findall(text):
        candidate = _resolve_reference(root, file, reference)
        if candidate is None or candidate.suffix.lower() not in IMAGE_EXTS:
            continue
        if not candidate.exists():
            raise ImageBuildError(f"{_display(root, candidate)}: image file not found")
        found.add(candidate.resolve())


def _keys(root: Path, path: Path) -> set[str]:
    """Every project path a developer may pass to `Image` for one source file."""
    keys = {normalize_source(_display(root, path))}
    for base in (root, root / "public"):
        try:
            keys.add(normalize_source(path.relative_to(base)))
        except ValueError:
            continue
    return {key for name in keys if name for key in (name, "/" + name)}


def _vite_aliases(root: Path, keys: set[str]) -> set[str]:
    """The hashed Vite URL of an imported image also resolves to its variants."""
    manifest = root / "__nexy__/client/.vite/manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if not isinstance(data, dict):
        return set()
    names = {key.lstrip("/") for key in keys}
    aliases = set()
    for source, entry in data.items():
        if normalize_source(source) not in names or not isinstance(entry, dict):
            continue
        file = entry.get("file")
        if isinstance(file, str):
            aliases.add("/" + file.lstrip("/"))
    return aliases


def _variants(path: Path, key: str, widths: list[int]) -> tuple[Variant, dict[str, bytes]] | None:
    """Resize one image to each configured width and encode it as WebP."""
    pillow = _pillow()
    if pillow is None:
        return None
    try:
        data = path.read_bytes()
        with pillow.open(io.BytesIO(data)) as original:
            natural_width, natural_height = original.size
            mode = "RGBA" if "A" in original.getbands() else "RGB"
            base = original.convert(mode)
        return _encode(base, data, key, natural_width, natural_height, widths, pillow)
    except (OSError, ValueError) as problem:
        raise ImageBuildError(f"{key}: cannot read image ({problem})") from problem


def _encode_files(
    base: Any,
    data: bytes,
    key: str,
    natural_width: int,
    natural_height: int,
    widths: list[int],
    pillow: Any,
) -> tuple[dict[str, bytes], list[tuple[int, str]]]:
    """Write each WebP variant and return its bytes and its srcset candidate."""
    targets = sorted({width for width in widths if width <= natural_width}) or [natural_width]
    files: dict[str, bytes] = {}
    candidates: list[tuple[int, str]] = []
    stem = re.sub(r"[^a-zA-Z0-9_-]", "-", Path(key).stem)
    for width in targets:
        height = max(1, round(natural_height * width / natural_width))
        buffer = io.BytesIO()
        resized = base.resize((width, height), pillow.Resampling.LANCZOS)
        resized.save(buffer, format="WEBP", quality=80)
        digest = hashlib.sha256(data + str(width).encode()).hexdigest()[:12]
        name = f"{stem}-{width}-{digest}.webp"
        files[name] = buffer.getvalue()
        candidates.append((width, "/images/" + name))
    return files, candidates


def _encode(
    base: Any,
    data: bytes,
    key: str,
    natural_width: int,
    natural_height: int,
    widths: list[int],
    pillow: Any,
) -> tuple[Variant, dict[str, bytes]]:
    """Describe the generated variants in a manifest record."""
    files, candidates = _encode_files(
        base, data, key, natural_width, natural_height, widths, pillow
    )
    largest_width, largest_url = candidates[-1]
    record: Variant = {
        "src": largest_url,
        "srcset": ", ".join(f"{url} {width}w" for width, url in candidates),
        "sizes": f"(max-width: {largest_width}px) 100vw, {largest_width}px",
        "width": natural_width,
        "height": natural_height,
    }
    return record, files


def prepare_images(root: Path | None = None, widths: list[int] | None = None) -> ImageBuild:
    """Compute every variant and its manifest without writing to the client bundle."""
    project = (root or Path.cwd()).resolve()
    configured = Config.useImageWidths
    default = DEFAULT_WIDTHS if configured is None else configured
    chosen = widths if widths is not None else default
    selected = list(chosen)
    sources = find_sources(project)
    source = _display(project, sources[0]) if sources else "nexyconfig.py"
    validate_widths(selected, source)
    build = ImageBuild({}, {})
    for path in sources:
        key = _display(project, path)
        result = _variants(path, key, selected)
        if result is None:
            continue
        variant, files = result
        aliases = _keys(project, path) | _vite_aliases(project, _keys(project, path))
        for alias in aliases:
            build.manifest[alias] = variant
        build.files.update(files)
    return build


def write_image_files(build: ImageBuild, root: Path | None = None) -> None:
    """Publish the generated files after Vite has emptied the client directory."""
    project = root or Path.cwd()
    directory = project / "__nexy__/client/images"
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in build.files.items():
        (directory / name).write_bytes(data)
