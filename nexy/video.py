import html


def _source_tag(path: str) -> str:
    """A `<source>` tag whose attributes cannot be broken out of by the path."""
    extension = path.split(".")[-1]
    return (
        f'<source src="{html.escape(path, quote=True)}" '
        f'type="video/{html.escape(extension, quote=True)}" />'
    )


def video(
    src: str,
    width: int | None = None,
    height: int | None = None,
    controls: bool = True,
    autoplay: bool = False,
    loop: bool = False,
    muted: bool = False,
    preload: str = "metadata",
    class_name: str | None = None,
    sources: list[str] | None = None,
    **kwargs: str | bool,
) -> str:
    """Render a native `<video>` player with optional sources.

    Args:
        src: Single video file path, used when `sources` is empty.
        width: Fixed width in pixels; omitted when None.
        height: Fixed height in pixels; omitted when None.
        controls: Add the native playback controls.
        autoplay: Start playback on load.
        loop: Restart playback at the end.
        muted: Start playback muted.
        preload: Value of the `preload` attribute (e.g. "metadata").
        class_name: CSS classes added to the element.
        sources: Multiple video paths rendered as `<source>` tags; the
            MIME type is derived from each file extension.
        **kwargs: Extra attributes merged into the element (`value=""`
            renders as a bare attribute).

    Returns:
        The `<video>` HTML markup ready to embed.
    """
    attrs: dict[str, str | bool] = {"preload": preload}
    if width is not None:
        attrs["width"] = str(width)
    if height is not None:
        attrs["height"] = str(height)
    if class_name:
        attrs["class"] = class_name
    if controls:
        attrs["controls"] = ""
    if autoplay:
        attrs["autoplay"] = ""
    if loop:
        attrs["loop"] = ""
    if muted:
        attrs["muted"] = ""

    attrs.update(kwargs)
    attr_str = " ".join(
        f'{k}="{html.escape(str(v), quote=True)}"' if v else k for k, v in attrs.items()
    )

    source_tags = ""
    if sources:
        for s in sources:
            source_tags += _source_tag(s)
    else:
        source_tags = _source_tag(src)

    return f"<video {attr_str}>{source_tags}</video>"
