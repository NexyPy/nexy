import pytest

from src.i18n import best, t


@pytest.mark.parametrize(
    ("header", "language"),
    [
        ("fr-FR,fr;q=0.9", "fr"),
        ("de, fr-CA;q=0.8, en;q=0.5", "fr"),
        ("en;q=0.2, fr;q=0.9", "fr"),
        ("de", "en"),
        ("", "en"),
        ("fr;q=0", "en"),
        ("fr;q=nonsense", "en"),
    ],
)
def test_best_picks_the_preferred_language_the_site_has(header, language):
    assert best(header) == language


def test_one_takes_the_singular():
    assert t("fr", "home.tables", count=1) == "1 table libre en ce moment."


def test_more_than_one_takes_the_plural():
    assert t("en", "home.tables", count=3) == "3 tables free right now."


def test_every_language_has_every_sentence():
    from src.i18n.catalog import MESSAGES

    assert {lang: set(m) for lang, m in MESSAGES.items()} == {
        lang: set(MESSAGES["en"]) for lang in MESSAGES
    }
