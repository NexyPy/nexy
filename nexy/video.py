from nexy.helpers.html.media import media_element, playback_attributes


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
    sizes = {"width": width, "height": height}
    attrs = playback_attributes(
        preload=preload,
        class_name=class_name,
        controls=controls,
        autoplay=autoplay,
        loop=loop,
        muted=muted,
        sizes={name: str(size) for name, size in sizes.items() if size is not None},
    )
    attrs.update(kwargs)
    return media_element("video", attrs, src, sources)
