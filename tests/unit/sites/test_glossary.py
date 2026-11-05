"""The words of the docs a service leaves in English when they stand alone in a link."""

from __future__ import annotations

import pytest

from sites.shared import glossary, i18n

OTHERS = [language.code for language in i18n.LANGUAGES if language.code != i18n.DEFAULT]


def test_term_translates_a_known_word():
    assert glossary.term("views", "fr") == "vues"


def test_term_capitalizes_like_the_english_word():
    assert glossary.term("Testing", "fr") == "Tests"


def test_the_order_names_every_language_of_the_site():
    assert sorted(glossary.ORDER) == sorted(OTHERS)


def test_term_keeps_a_german_noun_capitalized():
    assert glossary.term("views", "de") == "Ansichten"


def test_term_is_none_for_an_unknown_word():
    assert glossary.term("teapot", "fr") is None


def test_term_is_none_in_english():
    assert glossary.term("views", "en") is None


@pytest.mark.parametrize("english", sorted(glossary.TERMS))
def test_every_term_has_a_word_in_every_language(english):
    assert len(glossary.TERMS[english]) == len(OTHERS)


@pytest.mark.parametrize("english", sorted(glossary.TERMS))
def test_every_term_is_written_in_lower_case(english):
    assert english == english.lower()
