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
    attrs = {"preload": preload}
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
    attr_str = " ".join([f'{k}="{v}"' if v else k for k, v in attrs.items()])

    source_tags = ""
    if sources:
        for s in sources:
            source_tags += f'<source src="{s}" type="video/{s.split(".")[-1]}" />'
    else:
        source_tags = f'<source src="{src}" type="video/{src.split(".")[-1]}" />'

    return f"<video {attr_str}>{source_tags}</video>"
