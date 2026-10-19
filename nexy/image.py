def image(
    src: str,
    alt: str = "",
    width: int | None = None,
    height: int | None = None,
    loading: str = "lazy",
    class_name: str | None = None,
    **kwargs: str | int,
) -> str:
    attrs = {
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

    attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])

    return f"<img {attr_str} />"
