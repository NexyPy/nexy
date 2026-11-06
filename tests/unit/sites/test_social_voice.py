"""A caption is checked before it ships, and the heuristics never block."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sites.shared.social import Item, Kind, Media, voice


def _item(tmp_path: Path, **given: object) -> Item:
    facts: dict[str, object] = {
        "directory": tmp_path,
        "category": "posts",
        "slug": "2026-11-hmr",
        "lang": "en",
        "published": date(2026, 11, 6),
        "body": "47 ms.\n\nA route comes back in less time than a blink.",
        "platforms": ("linkedin",),
        "cta": "comment",
        **given,
    }
    return Item(**facts)  # type: ignore[arg-type]


def _proof(tmp_path: Path, name: str = "hmr-2026-11.md") -> None:
    (tmp_path / "proof").mkdir(exist_ok=True)
    (tmp_path / "proof" / name).write_text("# HMR\n")


def test_a_clean_caption_has_no_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    assert voice.check(_item(tmp_path, proof=("hmr-2026-11.md",)), tmp_path).ok()


def test_a_banned_word_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(tmp_path, body="47 ms. Seamless.", proof=("hmr-2026-11.md",)), tmp_path
    )
    assert "reads like every other caption" in report.errors[0]


def test_an_announcement_formula_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(tmp_path, body="47 ms.\n\nThis is why it matters.", proof=("hmr-2026-11.md",)),
        tmp_path,
    )
    assert "not a sentence" in report.errors[0]


def test_asking_for_engagement_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(tmp_path, body="47 ms.\n\nDrop a star if you like it.", proof=("hmr-2026-11.md",)),
        tmp_path,
    )
    assert "asks for engagement" in report.errors[0]


def test_an_emoji_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(tmp_path, body="47 ms \U0001f680", proof=("hmr-2026-11.md",)), tmp_path
    )
    assert "an emoji" in report.errors[0]


def test_a_hashtag_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(tmp_path, body="47 ms.\n\n#python", proof=("hmr-2026-11.md",)), tmp_path
    )
    assert "a hashtag" in report.errors[0]


def test_a_hook_over_ninety_characters_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(_item(tmp_path, body="a" * 91, proof=("hmr-2026-11.md",)), tmp_path)
    assert "the hook is 91 characters" in report.errors[0]


def test_a_number_without_a_proof_is_an_error(tmp_path: Path) -> None:
    report = voice.check(_item(tmp_path), tmp_path)
    assert "a number with no proof" in report.errors[0]


def test_a_proof_file_that_does_not_exist_is_an_error(tmp_path: Path) -> None:
    report = voice.check(_item(tmp_path, proof=("missing.md",)), tmp_path)
    assert "does not exist" in report.errors[0]


def test_a_post_on_a_network_needs_a_cta(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(_item(tmp_path, cta="", proof=("hmr-2026-11.md",)), tmp_path)
    assert "`cta` is required" in report.errors[0]


def test_an_unknown_ask_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(_item(tmp_path, ask="star", proof=("hmr-2026-11.md",)), tmp_path)
    assert "never star or follow" in report.errors[0]


def test_asking_for_a_report_needs_a_proof(tmp_path: Path) -> None:
    report = voice.check(_item(tmp_path, ask="report"), tmp_path)
    assert any("needs a `proof`" in error for error in report.errors)


def test_asking_to_contribute_needs_a_community_snapshot(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(_item(tmp_path, ask="contribute", proof=("hmr-2026-11.md",)), tmp_path)
    assert any("community snapshot" in error for error in report.errors)


def test_asking_to_contribute_is_accepted_with_a_snapshot(tmp_path: Path) -> None:
    _proof(tmp_path)
    _proof(tmp_path, "community-2026-11.md")
    report = voice.check(_item(tmp_path, ask="contribute", proof=("hmr-2026-11.md",)), tmp_path)
    assert report.ok()


def test_a_link_in_the_caption_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    link = "https://github.com/NexyPy/nexy"
    report = voice.check(
        _item(tmp_path, link=link, body=f"47 ms.\n\n{link}", proof=("hmr-2026-11.md",)), tmp_path
    )
    assert "a link costs reach" in report.errors[0]


def test_a_blog_without_a_canonical_is_an_error(tmp_path: Path) -> None:
    report = voice.check(
        _item(tmp_path, category="blogs", title="Why", description="Short."), tmp_path
    )
    assert any("`canonical`" in error for error in report.errors)


def test_a_description_over_one_hundred_sixty_characters_is_an_error(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(
            tmp_path,
            category="blogs",
            title="Why",
            description="a" * 161,
            canonical="https://example.test/why",
            tags=("python",),
            cover="cover.png",
            proof=("hmr-2026-11.md",),
        ),
        tmp_path,
    )
    assert "161 characters" in report.errors[0]


def test_a_blog_wants_one_to_four_tags(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(
        _item(
            tmp_path,
            category="blogs",
            title="Why",
            description="Short.",
            canonical="https://example.test/why",
            tags=(),
            cover="cover.png",
            proof=("hmr-2026-11.md",),
        ),
        tmp_path,
    )
    assert "0 tags" in report.errors[0]


def test_a_long_sentence_is_only_a_warning(tmp_path: Path) -> None:
    _proof(tmp_path)
    body = " ".join(["consequently"] * 40) + "."
    report = voice.check(_item(tmp_path, body=body, proof=("hmr-2026-11.md",)), tmp_path)
    assert report.warnings and not any("readab" in error for error in report.errors)


def test_a_post_without_media_is_only_a_warning(tmp_path: Path) -> None:
    _proof(tmp_path)
    report = voice.check(_item(tmp_path, proof=("hmr-2026-11.md",)), tmp_path)
    assert any("no media" in warning for warning in report.warnings)


def test_a_post_with_media_is_not_warned(tmp_path: Path) -> None:
    _proof(tmp_path)
    path = tmp_path / "01.png"
    path.write_bytes(b"x")
    media = Media(kind=Kind.IMAGE, files=(path,), alts=("one",))
    report = voice.check(_item(tmp_path, proof=("hmr-2026-11.md",), media=media), tmp_path)
    assert not any("no media" in warning for warning in report.warnings)


def test_hook_returns_the_first_non_empty_line() -> None:
    assert voice.hook("\n\n47 ms.\n\nMore.") == "47 ms."


def test_readability_of_an_empty_text_is_zero() -> None:
    assert voice.readability("") == 0.0


def test_two_invitations_in_four_posts_are_reported(tmp_path: Path) -> None:
    posts = [
        _item(tmp_path, slug=f"2026-11-{index}", published=date(2026, 11, index + 1), ask="run")
        for index in range(4)
    ]
    assert voice.density(posts)


def test_one_invitation_in_four_posts_is_accepted(tmp_path: Path) -> None:
    posts = [
        _item(tmp_path, slug=f"2026-11-{index}", published=date(2026, 11, index + 1))
        for index in range(4)
    ]
    posts[0] = _item(tmp_path, slug="2026-11-0", published=date(2026, 11, 1), ask="run")
    assert voice.density(posts) == []
