"""The rules a caption can be checked against, and the ones only a human can judge.

Two kinds of findings. An **error** is mechanical: a banned phrase, an emoji, a hashtag, a number
with no dated proof, a call to action that begs. A **warning** is a heuristic that can be wrong:
readability, two paragraphs of the same length, a post with no media. A rule that produces false
positives is a nuisance, not a rule, so the heuristics never block.

What no linter sees is written in `COM/VOICE.md`: a detail only someone who ran the code would
know, an admitted limit, a sentence that could sit in any other framework's post.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from sites.shared.social import Item, Kind

__all__ = ["ASK", "CTA", "HOOK", "Report", "check", "density", "hook", "readability"]

HOOK = 90
CTA = ("link", "comment", "none")
ASK = ("none", "run", "report", "contribute")
READING_GRADE = 10
DESCRIPTION = 160
TAGS = (1, 4)

# Words that make a caption read like every other caption. Not a detection tool: a reminder.
BANNED = (
    "delve",
    "seamless",
    "seamlessly",
    "game-chang",
    "cutting-edge",
    "revolutioni",
    "unlock",
    "unleash",
    "elevate",
    "empower",
    "robust",
    "state-of-the-art",
    "in today's",
    "dive into",
    "deep dive",
    "harness",
    "transformative",
    "supercharge",
    "effortless",
    "world-class",
    "next-level",
    "best-in-class",
    "tapestry",
    "testament",
    "the future of",
    "journey",
)

# The structures that give a machine away, more than any single word.
ANNOUNCE = (
    r"\bthis is why\b",
    r"\bit'?s not just\b",
    r"\bisn'?t just\b",
    r"\bnot only\b[^.]{0,80}\bbut also\b",
    r"\bhere'?s why\b",
    r"\bwhat if i told you\b",
)

# Asking for an engagement is harassment when the post has not given anything yet.
SOLICIT = (
    r"\b(drop|leave|give|hit|smash|add)\s+(us\s+)?(a|one|some)?\s*(star|stars|review)\b",
    r"\bstar\s+(us|the repo|this repo|the project|it)\b",
    r"\b(fork|follow|share|subscribe)\s+(us|me|for|the repo)\b",
    r"\bplease\s+(star|fork|follow|share|subscribe|retweet)\b",
    r"\bdon'?t forget to\b",
    r"\bif you (like|liked|enjoy|enjoyed|found this useful)\b",
    r"\bsupport\s+the\s+project\b",
    r"\bshare\s+(this|it)\b",
    r"\bhelp\s+us\s+grow\b",
    r"\bspread\s+the\s+word\b",
)

EMOJI = re.compile("[\U0001f300-\U0001faff\u2600-\u27bf\u2b00-\u2bff\ufe0f]")
HASHTAG = re.compile(r"(?<!\w)#\w+")
NUMBER = re.compile(r"\d")
SOLICIT_RE = tuple(re.compile(pattern, re.IGNORECASE) for pattern in SOLICIT)
ANNOUNCE_RE = tuple(re.compile(pattern, re.IGNORECASE) for pattern in ANNOUNCE)
VOWEL_GROUP = re.compile(r"[aeiouy]+")
WORD = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class Report:
    """What a caption breaks, and what it might break."""

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def ok(self) -> bool:
        """True when nothing mechanical is wrong, warnings included in the count or not."""
        return not self.errors


def check(item: Item, root: Path) -> Report:
    """Every rule this item breaks, and every heuristic it trips."""
    errors = list(_writing(item))
    errors.extend(_channels(item))
    errors.extend(_proof(item, root))
    errors.extend(_blog(item))
    return Report(errors=tuple(errors), warnings=tuple(_warnings(item)))


def density(items: Sequence[Item], window: int = 4) -> list[str]:
    """One invitation in four posts at most: past that, even a good invitation is a campaign."""
    posts = sorted((item for item in items if item.platforms), key=lambda item: item.published)
    return [
        f"{posts[index].name()}: {window} posts in a row already carry an `ask`, this one waits"
        for index in range(window - 1, len(posts))
        if sum(1 for item in posts[index - window + 1 : index + 1] if item.ask != "none") > 1
    ]


def hook(body: str) -> str:
    """The first line of a caption: the only one a feed shows before `see more`."""
    return next((line.strip() for line in body.splitlines() if line.strip()), "")


def readability(text: str) -> float:
    """Flesch-Kincaid grade, computed on the words only: a warning, never a gate."""
    sentences = max(1, len([part for part in re.split(r"[.!?]+", text) if part.strip()]))
    words = WORD.findall(text)
    if not words:
        return 0.0
    syllables = sum(len(VOWEL_GROUP.findall(word)) or 1 for word in words)
    return 0.39 * len(words) / sentences + 11.8 * syllables / len(words) - 15.59


def _writing(item: Item) -> list[str]:
    text = item.body
    lowered = text.lower()
    errors = [
        f"{item.name()}: `{word}` reads like every other caption"
        for word in BANNED
        if word in lowered
    ]
    errors.extend(_matches(item, ANNOUNCE_RE, "this is a formula, not a sentence"))
    errors.extend(_matches(item, SOLICIT_RE, "this asks for engagement before giving anything"))
    if EMOJI.search(text):
        errors.append(f"{item.name()}: an emoji, and the charte says none")
    if HASHTAG.search(text):
        errors.append(f"{item.name()}: a hashtag, and posts without hashtags reach further")
    if item.category == "posts" and len(hook(text)) > HOOK:
        errors.append(f"{item.name()}: the hook is {len(hook(text))} characters, {HOOK} at most")
    return errors


def _channels(item: Item) -> list[str]:
    errors: list[str] = []
    if item.platforms and item.cta not in CTA:
        errors.append(f"{item.name()}: `cta` is required, one of {', '.join(CTA)}")
    if item.ask not in ASK:
        errors.append(f"{item.name()}: `ask` is one of {', '.join(ASK)}, never star or follow")
    if item.ask == "report" and not item.proof:
        errors.append(f'{item.name()}: `ask = "report"` needs a `proof` to reproduce')
    if item.link and item.link in item.body:
        errors.append(f"{item.name()}: the link is in the caption, and a link costs reach")
    return errors


def _proof(item: Item, root: Path) -> list[str]:
    errors: list[str] = []
    if NUMBER.search(item.body) and not item.proof:
        errors.append(f'{item.name()}: a number with no proof, add `proof = ["<file>.md"]`')
    for name in item.proof:
        if not (root / "proof" / name).is_file():
            errors.append(f"{item.name()}: `proof/{name}` does not exist")
    if item.ask == "contribute" and not list((root / "proof").glob("community-*.md")):
        errors.append(f'{item.name()}: `ask = "contribute"` needs a dated community snapshot')
    return errors


def _blog(item: Item) -> list[str]:
    if item.category != "blogs":
        return []
    errors: list[str] = []
    if not item.title:
        errors.append(f"{item.name()}: a blog has a `title`")
    if not item.canonical:
        errors.append(
            f"{item.name()}: a blog has a `canonical`, so it never competes with the docs"
        )
    if not item.description:
        errors.append(f"{item.name()}: a blog has a `description`")
    elif len(item.description) > DESCRIPTION:
        errors.append(
            f"{item.name()}: the description is {len(item.description)} characters, "
            f"{DESCRIPTION} at most"
        )
    if not TAGS[0] <= len(item.tags) <= TAGS[1]:
        errors.append(f"{item.name()}: {len(item.tags)} tags, a blog wants {TAGS[0]} to {TAGS[1]}")
    if not item.cover:
        errors.append(f"{item.name()}: a blog has a `cover`, the image a reader sees first")
    return errors


def _warnings(item: Item) -> list[str]:
    warnings: list[str] = []
    if item.category == "posts" and readability(item.body) > READING_GRADE:
        warnings.append(f"{item.name()}: readability grade {readability(item.body):.1f}, aim lower")
    if _symmetric(item.body):
        warnings.append(f"{item.name()}: two paragraphs of the same length, check for symmetry")
    if item.category == "posts" and item.media is None:
        warnings.append(f"{item.name()}: no media, a text post reaches far less than a document")
    if item.media is not None and item.media.kind is Kind.VIDEO and not item.title:
        warnings.append(f"{item.name()}: a video reads better with a `title`")
    return warnings


def _matches(item: Item, patterns: tuple[re.Pattern[str], ...], why: str) -> list[str]:
    return [
        f"{item.name()}: `{pattern.pattern[:40]}`: {why}"
        for pattern in patterns
        if pattern.search(item.body)
    ]


def _symmetric(body: str) -> bool:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    for first, second in zip(paragraphs, paragraphs[1:], strict=False):
        longer, shorter = max(len(first), len(second)), min(len(first), len(second))
        if longer > 80 and shorter / longer > 0.9:
            return True
    return False
