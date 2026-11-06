"""Everything `COM/` holds, read, checked, packed and rehearsed. Nothing is ever sent.

    python scripts/publish_social.py --list
    python scripts/publish_social.py --check
    python scripts/publish_social.py --pack                 # every carousel
    python scripts/publish_social.py --pack 2026-11-six-routers
    python scripts/publish_social.py --dry-run --lang fr --platform linkedin

`--check` fails on a folder that is not `YYYY-MM-<slug>`, a frontmatter field we do not know, a
caption over the length a network accepts, a card that is the wrong shape, a number with no dated
proof, a hashtag, an emoji, a sentence that asks for engagement before giving anything. The
warnings it prints are heuristics: readability, symmetry, a post with no media. They never fail a
build, because a rule that is sometimes wrong is a nuisance, not a rule.

`--pack` writes `build/com/<slug>.pdf` and `build/com/<slug>-feed.png`: the document for LinkedIn
and the same cards at feed size. Neither is committed.

Publishing itself is manual on purpose: the access tokens of three networks are not something a
repository should hold. `--dry-run` prints exactly what a human then pastes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sites.shared.social import Item, cards, com, limits, state, utm, voice  # noqa: E402

COM = REPO / "COM"


def main(argv: list[str] | None = None) -> int:
    """Run one command over `COM/`, and say what it found."""
    args = _parser().parse_args(argv)
    root = Path(args.root)
    found = com.items(root)
    if args.list:
        return _list(found, root)
    if args.check:
        return _check(found, root)
    if args.pack is not None:
        return _pack(found, args.pack)
    if args.dry_run:
        return _dry_run(found, root, args.lang, args.platform)
    _parser().print_help()
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read, check, pack and rehearse the posts of COM/."
    )
    parser.add_argument("--root", default=str(COM), help="the COM folder (default: COM/)")
    parser.add_argument("--list", action="store_true", help="every item, one line each")
    parser.add_argument("--check", action="store_true", help="fail on anything that blocks a post")
    parser.add_argument(
        "--pack", nargs="?", const="", metavar="SLUG", help="carousel cards into one PDF"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print a caption and its tagged link"
    )
    parser.add_argument("--lang", default="en", help="the language of the dry run (default: en)")
    parser.add_argument("--platform", default="linkedin", help="the network of the dry run")
    return parser


def _list(found: list[Item], root: Path) -> int:
    published = state.load(root / state.STATE)
    for item in found:
        networks = ",".join(item.platforms) or "-"
        sent = sum(1 for platform in item.platforms if state.sent(published, item, platform))
        kind = item.media.kind.value if item.media else "text"
        print(f"{item.name():<44} {item.published} {kind:<8} {networks:<24} {sent} sent")
    print(f"\n{len(found)} item(s) in {root}")
    return 0 if found else 1


def _check(found: list[Item], root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for item in found:
        report = voice.check(item, root)
        errors.extend(report.errors)
        warnings.extend(report.warnings)
        errors.extend(limits.check(item))
        errors.extend(cards.check(item))
    errors.extend(voice.density(found))
    for message in warnings:
        print(f"  warning  {message}")
    for message in errors:
        print(f"  error    {message}")
    print(f"\n{len(found)} item(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 0 if not errors else 1


def _pack(found: list[Item], slug: str) -> int:
    with_cards = [item for item in found if item.media and item.media.kind.value == "carousel"]
    chosen = [item for item in with_cards if not slug or item.slug == slug]
    if not chosen:
        print(f"no carousel to pack{' for ' + slug if slug else ''}")
        return 1
    for item in chosen:
        document = cards.pack(item)
        sheet = cards.contact_sheet(item)
        print(f"{item.name()}: {document} and {sheet}")
    return 0


def _dry_run(found: list[Item], root: Path, lang: str, platform: str) -> int:
    chosen = [item for item in found if item.lang == lang and platform in item.platforms]
    if not chosen:
        print(f"nothing in {lang} for {platform}")
        return 1
    published = state.load(root / state.STATE)
    for item in chosen:
        link = utm.tagged(item.link, platform, item.slug, lang) if item.link else "(no link)"
        already = " [already sent]" if state.sent(published, item, platform) else ""
        print(f"--- {item.name()} on {platform}{already}\n{item.body}\n\n{link}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
