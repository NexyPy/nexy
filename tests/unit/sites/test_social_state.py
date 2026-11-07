"""A publication is marked once, per post, per language and per network."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sites.shared.social import Item, state


def _item(tmp_path: Path, lang: str = "en") -> Item:
    return Item(
        directory=tmp_path,
        category="posts",
        slug="2026-11-hmr",
        lang=lang,
        published=date(2026, 11, 6),
        body="47 ms.",
    )


def test_an_absent_file_means_nothing_was_published(tmp_path: Path) -> None:
    assert state.load(tmp_path / state.STATE) == {}


def test_the_key_names_the_post_the_language_and_the_network(tmp_path: Path) -> None:
    assert state.key(_item(tmp_path, "fr"), "linkedin") == "posts/2026-11-hmr/fr/linkedin"


def test_a_marked_publication_is_read_back_as_sent(tmp_path: Path) -> None:
    path = tmp_path / state.STATE
    state.save(path, state.mark({}, _item(tmp_path), "bluesky", "2026-11-06"))
    assert state.sent(state.load(path), _item(tmp_path), "bluesky")


def test_the_same_post_in_another_language_is_not_sent_yet(tmp_path: Path) -> None:
    marked = state.mark({}, _item(tmp_path, "en"), "linkedin", "2026-11-06")
    assert not state.sent(marked, _item(tmp_path, "fr"), "linkedin")


def test_saving_writes_sorted_keys(tmp_path: Path) -> None:
    path = tmp_path / state.STATE
    state.save(path, {"b": "2", "a": "1"})
    assert path.read_text().splitlines()[1].strip() == '"a": "1",'
