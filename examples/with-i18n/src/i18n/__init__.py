"""The languages of the site, and the language a visitor asks for.

Nexy has no locale layer: the language is the first part of the address (/en, /fr), and the
strings come from the plain dictionaries in `catalog.py`. Swap in gettext or Babel when the
catalog grows; the pages do not change.
"""

from src.i18n.catalog import MESSAGES

DEFAULT = "en"
# Each language by its own name: a visitor looks for the word they read.
LANGUAGES = {"en": "English", "fr": "Français"}


def best(accept_language: str) -> str:
    """The language of the site the visitor prefers, from an Accept-Language header such as
    `de, fr-CA;q=0.8, en;q=0.5` (here: fr). A language the site does not have is skipped."""
    ranked = []
    for part in accept_language.split(","):
        tag, _, quality = part.strip().partition(";q=")
        language = tag.split("-")[0].strip().lower()
        try:
            weight = float(quality) if quality else 1.0
        except ValueError:
            weight = 0.0
        if language in LANGUAGES and weight > 0:
            ranked.append((weight, language))
    return max(ranked, key=lambda pair: pair[0])[1] if ranked else DEFAULT


def t(language: str, key: str, count: int | None = None, **values: object) -> str:
    """The sentence `key` in `language`. With `count`, the plural form that fits it."""
    message = MESSAGES[language][key]
    if count is not None:
        message = message[0 if count == 1 else 1]
        values["count"] = count
    return message.format(**values)
