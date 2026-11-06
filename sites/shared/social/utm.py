"""Every link a post sends carries where it came from, or nothing is measurable.

GitHub Pages keeps no access log. Without a tag on the URL, a post that brought a hundred installs
looks exactly like a post that brought none: this module is the only reason a channel can be
judged, and the only reason to cut one.
"""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

__all__ = ["tagged"]

MEDIUM = "social"


def tagged(url: str, platform: str, slug: str, lang: str = "en") -> str:
    """The same URL with `utm_source`, `utm_medium`, `utm_campaign` and `utm_content`."""
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if not key.startswith("utm_")]
    query.extend(
        [
            ("utm_source", platform),
            ("utm_medium", MEDIUM),
            ("utm_campaign", slug),
            ("utm_content", lang),
        ]
    )
    return urlunsplit(parts._replace(query=urlencode(query)))
