import html


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
    attrs: dict[str, str | int] = {
        "src": src,
        "alt": alt,
        "loading": loading,
    }
    if width is not None:
        attrs["width"] = str(width)
    if height is not None:
        attrs["height"] = str(height)
    if class_name:
        attrs["class"] = class_name

    attrs.update(kwargs)

    attr_str = " ".join(f'{k}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())

    return f"<img {attr_str} />"
