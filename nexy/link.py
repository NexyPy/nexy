

def Link(
    href: str,
    children: str = "",
    class_name: str | None = None,
    prefetch: bool = True,
    **kwargs,
) -> str:
    # Build attributes
    attrs = {"href": href, "data-nexy-link": "true"}
    if class_name:
        attrs["class"] = class_name
    if prefetch:
        attrs["onmouseenter"] = f"window.__nexy_prefetch && window.__nexy_prefetch('{href}')"
        attrs["ontouchstart"] = f"window.__nexy_prefetch && window.__nexy_prefetch('{href}')"
    attrs.update(kwargs)

    # Convert attrs to HTML string
    attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])

    return f"<a {attr_str}>{children}</a>"
