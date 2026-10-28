"""The title and the head tags of a page, written by the layout from what the page said.

A page names them in its frontmatter, either as a literal or with a call:

    metadata = {"title": "Blog", "description": "Posts"}      # static
    setMetadata(title=post.title, og={"image": post.cover})   # dynamic

The root layout writes them once, escaped, with `{{ useMetadata().html() }}`. The page runs before
its layouts, so what it says is there when the layout asks; they live on the request, so one
request never sees another's.
"""

from __future__ import annotations

import html as _html
from dataclasses import dataclass, field, fields
from typing import Any

from nexy.core.config import Config
from nexy.hooks import useRequest

__all__ = ["Metadata", "setMetadata", "useMetadata"]


def _attributes(**attributes: str) -> str:
    return " ".join(
        f'{name}="{_html.escape(value, quote=True)}"' for name, value in attributes.items()
    )


def _meta(**attributes: str) -> str:
    return f"<meta {_attributes(**attributes)}>"


@dataclass
class Metadata:
    """What a page tells the browser and the search engines about itself."""

    title: str | None = None
    description: str | None = None
    canonical: str | None = None
    robots: str | None = None
    icon: str | None = None
    title_template: str | None = None
    og: dict[str, str] = field(default_factory=dict)
    twitter: dict[str, str] = field(default_factory=dict)
    extra: list[dict[str, str]] = field(default_factory=list)

    def merge(self, **given: Any) -> None:
        """Set the fields given: a dict or a list adds to what is there, a value replaces it."""
        known = {item.name for item in fields(self)}
        for name, value in given.items():
            if name not in known:
                raise TypeError(f"setMetadata() got an unexpected field '{name}'")
            current = getattr(self, name)
            if isinstance(current, dict):
                current.update(value)
            elif isinstance(current, list):
                current.extend(value)
            else:
                setattr(self, name, value)

    def _title(self) -> str:
        title = self.title or Config.useTitle
        shown = self.title_template % title if self.title and self.title_template else title
        return f"<title>{_html.escape(shown)}</title>"

    def _simple(self) -> list[str]:
        tags = []
        if self.description:
            tags.append(_meta(name="description", content=self.description))
        if self.robots:
            tags.append(_meta(name="robots", content=self.robots))
        if self.canonical:
            tags.append(f"<link {_attributes(rel='canonical', href=self.canonical)}>")
        if self.icon:
            tags.append(f"<link {_attributes(rel='icon', href=self.icon)}>")
        return tags

    def _prefixed(self) -> list[str]:
        graph = [_meta(property=f"og:{key}", content=value) for key, value in self.og.items()]
        cards = [_meta(name=f"twitter:{key}", content=value) for key, value in self.twitter.items()]
        return [*graph, *cards, *(_meta(**tag) for tag in self.extra)]

    def html(self) -> str:
        """The tags for the `<head>`, every value escaped; what is not set is not written."""
        return "\n".join([self._title(), *self._simple(), *self._prefixed()])


def useMetadata() -> Metadata:
    """Read the metadata of the current request, to write it in the layout.

    Returns:
        The request's `Metadata`: its fields, and `.html()` for the `<head>`.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    state = useRequest().state
    if not hasattr(state, "nexy_metadata"):
        state.nexy_metadata = Metadata()
    metadata: Metadata = state.nexy_metadata
    return metadata


def setMetadata(**given: Any) -> None:
    """Say what the current page is about; a later call adds to or replaces an earlier one.

    Args:
        **given: `title`, `description`, `canonical`, `robots`, `icon`, `title_template` (such
            as `"%s | My site"`), `og` and `twitter` (dicts, keys without the prefix) and `extra`
            (a list of attribute dicts, one `<meta>` each).

    Raises:
        RuntimeError: If called outside an HTTP request context.
        TypeError: If a field does not exist.
    """
    useMetadata().merge(**given)


def apply_static_metadata(literal: dict[str, Any]) -> None:
    """Apply the `metadata = {...}` literal of a page, when there is a request to apply it to.

    Called by the module the compiler writes. A page rendered outside a request, in a test for
    example, simply has no metadata to set.
    """
    try:
        setMetadata(**literal)
    except RuntimeError:
        return
