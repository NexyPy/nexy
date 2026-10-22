def link(
    href: str,
    children: str = "",
    class_name: str | None = None,
    prefetch: bool = True,
    **kwargs: str | bool,
) -> str:
    """Render a client-side `<a>` link with optional prefetch hooks.

    Args:
        href: Target URL handled by the client router (`data-nexy-link`).
        children: Inner text of the anchor.
        class_name: CSS classes added to the anchor.
        prefetch: Attach mouseenter/touchstart listeners to the built-in
            prefetch pipeline.
        **kwargs: Extra attributes merged into the anchor.

    Returns:
        The `<a>` HTML markup ready to embed.
    """
    attrs: dict[str, str | bool] = {"href": href, "data-nexy-link": "true"}
    if class_name:
        attrs["class"] = class_name
    if prefetch:
        attrs["onmouseenter"] = f"window.__nexy_prefetch && window.__nexy_prefetch('{href}')"
        attrs["ontouchstart"] = f"window.__nexy_prefetch && window.__nexy_prefetch('{href}')"
    attrs.update(kwargs)

    attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])

    return f"<a {attr_str}>{children}</a>"
