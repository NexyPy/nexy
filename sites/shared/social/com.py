"""Read `COM/`: the frontmatter, the body, the media and the language variants.

A folder is named `YYYY-MM-<slug>`, inside `COM/posts/` or `COM/blogs/`. Its files are
`post.md`, `post.fr.md`, `post.pt.md` (or `blog.md` and its variants). The kind of media is read
from what is inside the folder, never declared: `carousel/*.png`, `video.<ext>` or `image.<ext>`.
One folder ships one kind, which is why two kinds in one folder is an error rather than a choice.
"""

from __future__ import annotations

import re
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sites.shared.social import CATEGORIES, ComError, Item, Kind, Media

__all__ = [
    "BLOG_KEYS",
    "DEFAULT_LANG",
    "LANGUAGES",
    "POST_KEYS",
    "items",
    "kind_of",
    "read_item",
    "split",
    "variants",
]

LANGUAGES = ("en", "fr", "de", "es", "pt", "ru", "zh", "hi", "ar", "bn", "id", "ur")
DEFAULT_LANG = "en"

DELIMITER = "+++"
SLUG = re.compile(r"^\d{4}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
LANG_SUFFIX = re.compile(r"^[a-z]{2}$")
STEMS = ("post", "blog")

POST_KEYS = frozenset({"date", "platforms", "link", "cta", "ask", "proof", "alt", "title"})
BLOG_KEYS = frozenset(
    {"date", "title", "description", "tags", "canonical", "cover", "cta", "ask", "proof"}
)

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif")
VIDEO_SUFFIXES = (".mp4", ".webm", ".mov")


def split(text: str) -> tuple[dict[str, Any], str]:
    """Return the frontmatter and the body of a `COM/` file, both without the delimiters."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != DELIMITER:
        raise ComError(f"the file must start with `{DELIMITER}`, not with {lines[:1] or 'nothing'}")
    try:
        end = lines.index(DELIMITER, 1)
    except ValueError:
        raise ComError(f"the frontmatter has no closing `{DELIMITER}`") from None
    try:
        meta = tomllib.loads("\n".join(lines[1:end]))
    except tomllib.TOMLDecodeError as error:
        raise ComError(f"the frontmatter is not valid TOML: {error}") from error
    return meta, "\n".join(lines[end + 1 :]).strip()


def variants(directory: Path, stem: str) -> list[Path]:
    """Every language variant of one item, `post.md` included, sorted by language code."""
    found = [path for path in sorted(directory.glob(f"{stem}*.md")) if _lang_of(path, stem)]
    return found


def items(root: Path) -> list[Item]:
    """Every item of `COM/`, both categories and every language, sorted by slug then language."""
    found: list[Item] = []
    for category in CATEGORIES:
        folder = root / category
        if not folder.is_dir():
            continue
        for directory in sorted(path for path in folder.iterdir() if path.is_dir()):
            for stem in STEMS:
                found.extend(read_item(path) for path in variants(directory, stem))
    return found


def kind_of(directory: Path) -> Kind | None:
    """The one kind of media a folder ships, or None for a text-only post."""
    found: set[Kind] = set()
    if _carousel_files(directory):
        found.add(Kind.CAROUSEL)
    if _media_files(directory, "image", IMAGE_SUFFIXES):
        found.add(Kind.IMAGE)
    if _media_files(directory, "video", VIDEO_SUFFIXES):
        found.add(Kind.VIDEO)
    if len(found) > 1:
        names = ", ".join(sorted(kind.value for kind in found))
        raise ComError(f"{directory.name}: two kinds of media ({names}), keep one")
    return found.pop() if found else None


def read_item(path: Path) -> Item:
    """Read one file of `COM/` into an item, or say exactly what is wrong with it."""
    directory = path.parent
    category = _category(directory)
    stem, lang = _stem_and_lang(path)
    meta, body = split(path.read_text(encoding="utf-8"))
    _reject_unknown(meta, category, path)
    return Item(
        directory=directory,
        category=category,
        slug=_slug(directory),
        lang=lang,
        published=_published(meta.get("date"), path),
        body=body,
        title=_text(meta.get("title"), "title", path),
        description=_text(meta.get("description"), "description", path),
        platforms=_tuple(meta.get("platforms"), "platforms", path),
        link=_text(meta.get("link"), "link", path),
        cta=_text(meta.get("cta"), "cta", path) or "none",
        ask=_text(meta.get("ask"), "ask", path) or "none",
        proof=_tuple(meta.get("proof"), "proof", path),
        tags=_tuple(meta.get("tags"), "tags", path),
        canonical=_text(meta.get("canonical"), "canonical", path),
        cover=_text(meta.get("cover"), "cover", path),
        media=None if category == "blogs" else _media(directory, meta, path),
        stem=stem,
    )


def _category(directory: Path) -> str:
    category = directory.parent.name
    if category not in CATEGORIES:
        raise ComError(f"{directory}: a folder must sit in one of {', '.join(CATEGORIES)}")
    return category


def _slug(directory: Path) -> str:
    if not SLUG.match(directory.name):
        raise ComError(f"{directory.name}: a folder is named YYYY-MM-<slug>, in lowercase")
    return directory.name


def _stem_and_lang(path: Path) -> tuple[str, str]:
    for stem in STEMS:
        lang = _lang_of(path, stem)
        if lang:
            return stem, lang
    raise ComError(
        f"{path.name}: the file is named post.md, post.<lang>.md, blog.md or blog.<lang>.md"
    )


def _lang_of(path: Path, stem: str) -> str | None:
    """The language of `post.fr.md`; `en` for `post.md`; None when the name is something else."""
    if not path.name.startswith(stem):
        return None
    suffix = path.stem[len(stem) :].removeprefix(".")
    if not suffix:
        return DEFAULT_LANG
    if not LANG_SUFFIX.match(suffix):
        return None
    if suffix not in LANGUAGES:
        raise ComError(f"{path.name}: {suffix!r} is not one of the {len(LANGUAGES)} site languages")
    return suffix


def _reject_unknown(meta: dict[str, Any], category: str, path: Path) -> None:
    known = BLOG_KEYS if category == "blogs" else POST_KEYS
    unknown = sorted(set(meta) - known)
    if unknown:
        raise ComError(f"{path.name}: unknown frontmatter field(s) {', '.join(unknown)}")


def _published(value: Any, path: Path) -> date:
    if isinstance(value, datetime):
        raise ComError(f"{path.name}: `date` is a date (2026-11-06), not a datetime")
    if not isinstance(value, date):
        raise ComError(f"{path.name}: `date` is required, as 2026-11-06")
    return value


def _text(value: Any, field: str, path: Path) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ComError(f"{path.name}: `{field}` is a string")
    return value.strip() or None


def _tuple(value: Any, field: str, path: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raise ComError(f"{path.name}: `{field}` is an array, not a string")
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        raise ComError(f"{path.name}: `{field}` is an array of strings")
    return tuple(value)


def _media(directory: Path, meta: dict[str, Any], path: Path) -> Media | None:
    kind = kind_of(directory)
    if kind is None:
        return None
    files = (
        _carousel_files(directory) if kind is Kind.CAROUSEL else _media_files_of(directory, kind)
    )
    return Media(kind=kind, files=tuple(files), alts=_alts(meta.get("alt"), path))


def _alts(value: Any, path: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(entry, str) for entry in value):
        return tuple(value)
    raise ComError(f"{path.name}: `alt` is a string, or an array with one string per card")


def _carousel_files(directory: Path) -> list[Path]:
    cards = directory / "carousel"
    return sorted(cards.glob("*.png")) if cards.is_dir() else []


def _media_files(directory: Path, name: str, suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(path for path in directory.glob(f"{name}.*") if path.suffix.lower() in suffixes)


def _media_files_of(directory: Path, kind: Kind) -> list[Path]:
    name, suffixes = ("image", IMAGE_SUFFIXES) if kind is Kind.IMAGE else ("video", VIDEO_SUFFIXES)
    found = _media_files(directory, name, suffixes)
    if len(found) > 1:
        raise ComError(f"{directory.name}: {len(found)} {name} files, keep one")
    return found
