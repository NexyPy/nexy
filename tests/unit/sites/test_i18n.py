"""The languages of the two sites: twelve of them, one payload, one picker, one version badge."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from nexy.__version__ import __version__
from sites.shared import docs_source, i18n, version
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

    def test_each_language_links_to_the_same_page_in_that_language(self):
        html = i18n.select_html("en", lambda code: f"/docs/{code}/guides/actions/")
        assert 'href="/docs/de/guides/actions/"' in html


class TestLocalize:
    def test_a_word_of_the_site_is_written_in_the_language(self):
        html = i18n.localize('<span data-i18n="search">Search</span>', "fr")
        assert html == '<span data-i18n="search">Rechercher</span>'

    def test_a_label_is_written_in_the_language(self):
        html = i18n.localize('<button aria-label="Search the docs" data-i18n-aria="search">', "fr")
        assert 'aria-label="Rechercher"' in html

    def test_a_placeholder_is_written_in_the_language(self):
        html = i18n.localize('<input placeholder="Search" data-i18n-placeholder="search">', "fr")
        assert 'placeholder="Rechercher"' in html

    def test_english_leaves_the_page_untouched(self):
        html = '<span data-i18n="search">Look</span>'
        assert i18n.localize(html, "en") == html


class TestVanilla:
    def test_the_build_writes_the_payload(self, out):
        payload = json.loads((out / "assets" / "i18n.json").read_text(encoding="utf-8"))
        assert set(payload) == {"languages", "ui"}

    def test_a_page_carries_the_picker(self, out):
        page = (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")
        picker = page.split('class="lang-select"', 1)[1].split("</details>", 1)[0]
        assert picker.count("data-lang=") == 12

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
        assert f'<span class="side-version" aria-label="Nexy {version.VERSION}">' in page

    def test_the_version_badge_names_the_package_line(self):
        major, minor, *_ = __version__.split(".")
        assert f"V{major}.{minor}" == version.VERSION


class TestPreferred:
    def test_the_first_known_language_of_the_browser_wins(self):
        assert i18n.preferred("xx, fr-CA;q=0.9, de;q=0.8") == "fr"

    def test_a_browser_that_asks_for_nothing_known_reads_english(self):
        assert i18n.preferred("xx, yy") == "en"

    def test_no_header_reads_english(self):
        assert i18n.preferred("") == "en"


class TestIsolate:
    def test_a_code_heading_on_an_arabic_page_reads_left_to_right(self):
        assert i18n.isolate("src/routes/", "ar") == ' dir="ltr"'

    def test_an_arabic_heading_keeps_the_page_direction(self):
        assert i18n.isolate("المستوى الأعلى", "ar") == ""

    def test_a_left_to_right_page_needs_nothing(self):
        assert i18n.isolate("src/routes/", "fr") == ""


class TestLocalizeEveryAttribute:
    def test_a_tag_with_a_label_and_a_placeholder_gets_both(self):
        tag = (
            '<input placeholder="Search" aria-label="Search"'
            ' data-i18n-placeholder="search" data-i18n-aria="search_aria">'
        )
        html = i18n.localize(tag, "fr")
        assert 'placeholder="Rechercher"' in html and 'aria-label="Rechercher dans' in html


# The English words of the site around a page: none of them may survive on a German page, a
# language where none of them is spelled the same.
CHROME = (
    'aria-label="Nexy, home"',
    'aria-label="Documentation"',
    'aria-label="Pages"',
    'aria-label="Nexy on GitHub"',
    'aria-label="Search the docs"',
    'aria-label="Link to this section"',
    ">New<",
    "<b>Modular</b>",
    "<b>Custom Integration</b>",
    'data-i18n="callout_note">Note<',
)


@pytest.mark.parametrize("english", CHROME)
def test_a_german_page_keeps_no_english_word_of_the_site(out, english):
    pages = [out / "docs" / "de" / "guides" / "actions" / "index.html"]
    pages += [out / "docs" / "de" / "reference" / "cli" / "index.html"]
    assert not any(english in page.read_text(encoding="utf-8") for page in pages)
