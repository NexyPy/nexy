"""The languages of the two sites: twelve of them, one payload, one picker, one version badge."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sites.shared import docs_source, home_strings, i18n, version
from sites.vanilla import build

DOCS = Path(__file__).resolve().parents[3] / "docs"
CODES = [language.code for language in i18n.LANGUAGES]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("i18n")
    build.build(target)
    return target


class TestLanguages:
    def test_twelve_languages_are_offered(self):
        assert len(i18n.LANGUAGES) == 12

    def test_every_code_is_unique(self):
        assert len(CODES) == len(set(CODES))

    def test_arabic_and_urdu_read_right_to_left(self):
        assert [one.code for one in i18n.LANGUAGES if one.direction == "rtl"] == ["ar", "ur"]

    def test_an_unknown_code_falls_back_to_english(self):
        assert i18n.find("xx").code == "en" and not i18n.is_known("xx")

    def test_every_language_translates_every_word(self):
        keys = set(i18n.UI["en"])
        assert all(set(block) == keys for block in i18n.UI.values())


class TestPayload:
    @pytest.fixture(scope="class")
    def payload(self) -> dict[str, object]:
        return i18n.payload()

    def test_the_payload_lists_every_language(self, payload):
        assert [one["code"] for one in payload["languages"]] == CODES

    def test_the_payload_carries_the_hero_of_every_language(self, payload):
        assert set(payload["home"]["hero"]) == set(CODES)

    def test_every_language_names_the_three_groups_of_the_home(self, payload):
        expected = {"first-steps", "understand-the-model", "coming-from-elsewhere"}
        assert all(set(groups) == expected for groups in payload["home"]["groups"].values())

    def test_every_language_has_a_card_for_every_page(self, payload):
        slugs = {page.slug for page in docs_source.pages_of(docs_source.read_tracks(DOCS)[0])}
        assert all(set(cards) == slugs for cards in payload["home"]["cards"].values())

    def test_the_payload_is_json_ready(self, payload):
        assert json.loads(json.dumps(payload))["ui"]["fr"]["search"] == "Rechercher"


class TestSelector:
    def test_the_picker_names_every_language_in_its_own_words(self):
        html = i18n.select_html()
        assert all(one.native in html for one in i18n.LANGUAGES)

    def test_the_picker_marks_the_current_language(self):
        html = i18n.select_html("fr")
        assert 'data-lang="fr"' in html and 'aria-current="true"' in html.split('data-lang="fr"')[1]
        assert "data-lang-code>FR<" in html


class TestVanilla:
    def test_the_build_writes_the_payload(self, out):
        payload = json.loads((out / "assets" / "i18n.json").read_text(encoding="utf-8"))
        assert set(payload) == {"languages", "ui", "home"}

    def test_a_page_carries_the_picker(self, out):
        page = (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")
        assert 'class="lang-select"' in page and page.count("data-lang=") == 12

    def test_a_page_says_where_the_payload_lives(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert 'data-i18n="' in page and "assets/i18n.json" in page

    def test_the_home_cards_name_their_page(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        found = set(re.findall(r'class="home-card" href="[^"]+" data-card="([^"]+)"', page))
        slugs = {p.slug for p in docs_source.pages_of(docs_source.read_tracks(DOCS)[0])}
        assert found == slugs

    def test_the_version_sits_next_to_the_logo(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert f'<span class="side-version" aria-label="Nexy version {version.VERSION}">' in page
        assert version.VERSION == "V2.2"


def test_the_home_translations_cover_every_language():
    assert set(home_strings.HERO) == set(CODES)
