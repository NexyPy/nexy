"""`COM/` is read from the disk: the frontmatter, the body, the media and the languages."""

from __future__ import annotations

from pathlib import Path

import pytest

from sites.shared.social import ComError, Kind, com


def _post(
    root: Path, folder: str = "2026-11-hmr", frontmatter: str = "", body: str = "47 ms."
) -> Path:
    directory = root / "posts" / folder
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "post.md"
    path.write_text(f"+++\ndate = 2026-11-06\n{frontmatter}+++\n\n{body}\n", encoding="utf-8")
    return path


def test_split_returns_the_frontmatter_and_the_body() -> None:
    meta, body = com.split("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    assert (meta["date"].isoformat(), body) == ("2026-11-06", "47 ms.")


def test_split_rejects_a_file_without_the_opening_delimiter() -> None:
    with pytest.raises(ComError, match="must start with"):
        com.split("47 ms.\n")


def test_split_rejects_an_unclosed_frontmatter() -> None:
    with pytest.raises(ComError, match="no closing"):
        com.split("+++\ndate = 2026-11-06\n\n47 ms.\n")


def test_split_rejects_invalid_toml() -> None:
    with pytest.raises(ComError, match="not valid TOML"):
        com.split("+++\ndate = \n+++\n\n47 ms.\n")


def test_variants_finds_every_language_of_one_item(tmp_path: Path) -> None:
    path = _post(tmp_path)
    (path.parent / "post.fr.md").write_text("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    assert [found.name for found in com.variants(path.parent, "post")] == ["post.fr.md", "post.md"]


def test_variants_rejects_a_two_letter_name_that_is_not_a_language(tmp_path: Path) -> None:
    path = _post(tmp_path)
    (path.parent / "post.jp.md").write_text("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    with pytest.raises(ComError, match="not one of the"):
        com.variants(path.parent, "post")


def test_kind_of_reads_the_carousel_folder(tmp_path: Path) -> None:
    directory = tmp_path / "posts" / "2026-11-cards"
    (directory / "carousel").mkdir(parents=True)
    (directory / "carousel" / "01.png").write_bytes(b"x")
    assert com.kind_of(directory) is Kind.CAROUSEL


def test_kind_of_rejects_two_kinds_in_one_folder(tmp_path: Path) -> None:
    directory = tmp_path / "posts" / "2026-11-both"
    (directory / "carousel").mkdir(parents=True)
    (directory / "carousel" / "01.png").write_bytes(b"x")
    (directory / "image.png").write_bytes(b"x")
    with pytest.raises(ComError, match="two kinds"):
        com.kind_of(directory)


def test_read_item_reads_a_post(tmp_path: Path) -> None:
    path = _post(tmp_path, frontmatter='platforms = ["linkedin"]\ncta = "comment"\n')
    item = com.read_item(path)
    assert (item.slug, item.lang, item.category, item.cta) == (
        "2026-11-hmr",
        "en",
        "posts",
        "comment",
    )


def test_read_item_reads_the_language_of_a_variant(tmp_path: Path) -> None:
    path = _post(tmp_path)
    (path.parent / "post.fr.md").write_text("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    assert com.read_item(path.parent / "post.fr.md").lang == "fr"


def test_read_item_rejects_an_unknown_frontmatter_field(tmp_path: Path) -> None:
    path = _post(tmp_path, frontmatter='hashtags = ["python"]\n')
    with pytest.raises(ComError, match="unknown frontmatter field"):
        com.read_item(path)


def test_read_item_rejects_a_folder_that_is_not_named_yyyy_mm_slug(tmp_path: Path) -> None:
    path = _post(tmp_path, folder="HMR")
    with pytest.raises(ComError, match="YYYY-MM"):
        com.read_item(path)


def test_read_item_rejects_a_language_that_the_site_does_not_publish(tmp_path: Path) -> None:
    path = _post(tmp_path)
    (path.parent / "post.jp.md").write_text("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    with pytest.raises(ComError, match="not one of the"):
        com.read_item(path.parent / "post.jp.md")


def test_read_item_rejects_a_datetime_instead_of_a_date(tmp_path: Path) -> None:
    path = _post(tmp_path)
    path.write_text("+++\ndate = 2026-11-06T10:00:00\n+++\n\n47 ms.\n")
    with pytest.raises(ComError, match="not a datetime"):
        com.read_item(path)


def test_read_item_rejects_two_image_files(tmp_path: Path) -> None:
    path = _post(tmp_path)
    (path.parent / "image.png").write_bytes(b"x")
    (path.parent / "image.webp").write_bytes(b"x")
    with pytest.raises(ComError, match="keep one"):
        com.read_item(path)


def test_read_item_wants_one_alt_per_card(tmp_path: Path) -> None:
    path = _post(tmp_path, frontmatter='alt = ["first", "second"]\n')
    (path.parent / "carousel").mkdir()
    for name in ("01.png", "02.png"):
        (path.parent / "carousel" / name).write_bytes(b"x")
    assert com.read_item(path).media.alts == ("first", "second")  # type: ignore[union-attr]


def test_items_lists_the_language_variants_of_both_categories(tmp_path: Path) -> None:
    post = _post(tmp_path)
    (post.parent / "post.fr.md").write_text("+++\ndate = 2026-11-06\n+++\n\n47 ms.\n")
    blog = tmp_path / "blogs" / "2026-11-why"
    blog.mkdir(parents=True)
    (blog / "blog.md").write_text("+++\ndate = 2026-11-06\ntitle = 'Why'\n+++\n\nBody.\n")
    assert len(com.items(tmp_path)) == 3
