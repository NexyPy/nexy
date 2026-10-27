from nexy.helpers.html.media import media_element, playback_attributes


def audio(
    src: str,
    controls: bool = True,
    autoplay: bool = False,
    loop: bool = False,
    muted: bool = False,
    preload: str = "metadata",
    class_name: str | None = None,
    sources: list[str] | None = None,
    **kwargs: str | bool,
) -> str:
    """Render a native `<audio>` player with optional sources.

    Args:
        src: Single audio file path, used when `sources` is empty.
        controls: Add the native playback controls.
        autoplay: Start playback on load.
        loop: Restart playback at the end.
        muted: Start playback muted.
        preload: Value of the `preload` attribute (e.g. "metadata").
        class_name: CSS classes added to the `<audio>` element.
        sources: Multiple audio paths rendered as `<source>` tags; the
            MIME type is derived from each file extension.
        **kwargs: Extra attributes merged into the element (`value=""`
            renders as a bare attribute).

    Returns:
        The `<audio>` HTML markup ready to embed.
    """
    attrs = playback_attributes(
        preload=preload,
        class_name=class_name,
        controls=controls,
        autoplay=autoplay,
        loop=loop,
        muted=muted,
    )
    attrs.update(kwargs)
    return media_element("audio", attrs, src, sources)
