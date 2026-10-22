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
    attrs: dict[str, str | bool] = {"preload": preload}
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
    attr_str = " ".join([f'{k}="{v}"' if v else k for k, v in attrs.items()])

    source_tags = ""
    if sources:
        for s in sources:
            source_tags += f'<source src="{s}" type="audio/{s.split(".")[-1]}" />'
    else:
        source_tags = f'<source src="{src}" type="audio/{src.split(".")[-1]}" />'

    return f"<audio {attr_str}>{source_tags}</audio>"
