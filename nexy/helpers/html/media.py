"""`<audio>` and `<video>`: the part of the two elements that is the same."""

from __future__ import annotations

import html

Attributes = dict[str, str | bool]


def source_tag(kind: str, path: str) -> str:
    """A `<source>` tag whose attributes cannot be broken out of by the path."""
    extension = path.split(".")[-1]
    return (
        f'<source src="{html.escape(path, quote=True)}" '
        f'type="{kind}/{html.escape(extension, quote=True)}" />'
    )


def source_tags(kind: str, src: str, sources: list[str] | None) -> str:
    """One tag per entry of *sources*, or a single tag for *src* when there are none."""
    return "".join(source_tag(kind, path) for path in (sources or [src]))


def playback_attributes(
    *,
    preload: str,
    class_name: str | None,
    controls: bool,
    autoplay: bool,
    loop: bool,
    muted: bool,
    sizes: Attributes | None = None,
) -> Attributes:
    """The attributes both players share; a flag that is off is left out."""
    attrs: Attributes = {"preload": preload, **(sizes or {})}
    if class_name:
        attrs["class"] = class_name
    flags = {"controls": controls, "autoplay": autoplay, "loop": loop, "muted": muted}
    attrs.update({name: "" for name, on in flags.items() if on})
    return attrs


def render_attributes(attrs: Attributes) -> str:
    """``name="value"`` pairs, escaped; an empty value is a bare attribute."""
    return " ".join(
        f'{name}="{html.escape(str(value), quote=True)}"' if value else name
        for name, value in attrs.items()
    )


def media_element(kind: str, attrs: Attributes, src: str, sources: list[str] | None) -> str:
    """The whole element: its attributes, then its `<source>` tags."""
    return f"<{kind} {render_attributes(attrs)}>{source_tags(kind, src, sources)}</{kind}>"
