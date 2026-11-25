import html

from nexy.core.config import Config
from nexy.modules.images.manifest import Variant, load_manifest, normalize_source
from nexy.modules.routers.base_path import public_url


def _candidate(src: str) -> Variant | None:
    """The generated variants of a local image, when `nx build` has seen it."""
    return load_manifest(Config.PROJECT_ROOT).get(normalize_source(src))


def _prefixed_srcset(value: str) -> str:
    """Prefix every URL in a `srcset`, without touching its width descriptors."""
    candidates = []
    for candidate in value.split(","):
        url, *descriptors = candidate.strip().split()
        candidates.append(" ".join([public_url(url), *descriptors]))
    return ", ".join(candidates)


def _variant_attributes(
    attrs: dict[str, str | int], src: str, width: int | None, height: int | None
) -> str:
    """Add the generated attributes and return the URL the browser should request."""
    variant = _candidate(src)
    if variant is None:
        return src
    attrs["srcset"] = _prefixed_srcset(str(variant["srcset"]))
    attrs["sizes"] = str(variant["sizes"])
    if width is None:
        attrs["width"] = variant["width"]
    if height is None:
        attrs["height"] = variant["height"]
    return str(variant["src"])


def image(
    src: str,
    alt: str = "",
    width: int | None = None,
    height: int | None = None,
    loading: str = "lazy",
    class_name: str | None = None,
    **kwargs: str | int,
) -> str:
    """Render an `<img>` element with lazy loading by default.

    Args:
        src: Image URL or path.
        alt: Alternative text (empty by default).
        width: Fixed width in pixels; omitted when None.
        height: Fixed height in pixels; omitted when None.
        loading: Loading strategy, "lazy" by default.
        class_name: CSS classes added to the element.
        **kwargs: Extra attributes merged into the element.

    Returns:
        The `<img>` HTML markup ready to embed.
    """
    attrs: dict[str, str | int] = {"src": src, "alt": alt, "loading": loading}
    attrs["src"] = public_url(_variant_attributes(attrs, src, width, height))
    if width is not None:
        attrs["width"] = str(width)
    if height is not None:
        attrs["height"] = str(height)
    if class_name:
        attrs["class"] = class_name
    if "srcSet" in kwargs:
        kwargs["srcset"] = kwargs.pop("srcSet")

    attrs.update(kwargs)

    attr_str = " ".join(f'{k}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())

    return f"<img {attr_str} />"
