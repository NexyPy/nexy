"""The vanilla site is plain files: every page exists, every link resolves, search finds each."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sites.shared import docs_source, i18n, seo
from sites.vanilla import build

DOCS = Path(__file__).resolve().parents[3] / "docs"


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("vanilla")
    build.build(target)
    return target


TRANSLATED = {language.code for language in i18n.LANGUAGES} - {i18n.DEFAULT}


def _english(name: str) -> bool:
    """Whether a path under docs/ of the site is an English page, not one of a language."""
    parts = Path(name).parts
    return not (len(parts) > 1 and parts[0] == "docs" and parts[1] in TRANSLATED)


def _pages(out: Path) -> list[Path]:
    """The English pages of the menu: a redirect is served at an old address, it is not a page."""
    redirects = {f"docs/{slug}" for slug in docs_source.REDIRECTS}
    return sorted(
        page
        for page in (out / "docs").rglob("index.html")
        if page.parent.relative_to(out).as_posix() not in redirects
        and _english(page.relative_to(out).as_posix())
    )


def _published(docs: Path) -> int:
    """The pages a crawler is told about: every English page and every real translation."""
    count = 0
    for language in i18n.LANGUAGES:
        tracks = docs_source.read_tracks(docs, language.code)
        pages = [docs_source.home(docs, language.code)]
        pages += [page for track in tracks for page in docs_source.pages_of(track)]
        count += sum(1 for page in pages if not page.fallback)
    return count


def _served_html(out: Path) -> dict[str, str]:
    """Every HTML the build wrote: its path inside the site, and its exact bytes."""
    return {
        p.relative_to(out).as_posix(): p.read_text(encoding="utf-8") for p in out.rglob("*.html")
    }


class TestPages:
    def test_every_doc_has_a_page(self, out):
        tracks = docs_source.read_tracks(DOCS)
        slugs = {p.slug for t in tracks for p in docs_source.pages_of(t)} | {""}
        found = {p.parent.relative_to(out / "docs").as_posix() for p in _pages(out)} - {"."}
        found.add("")
        assert found == slugs

    def test_the_root_sends_visitors_to_the_docs(self, out):
        assert 'url=docs/"' in (out / "index.html").read_text(encoding="utf-8")

    def test_github_pages_does_not_run_jekyll(self, out):
        assert (out / ".nojekyll").is_file()

    def test_the_assets_are_copied(self, out):
        assert all((out / "assets" / name).is_file() for name in ("style.css", "site.js"))


class TestHomePage:
    """The home page is a first path: the introduction, then the cards of Getting Started."""

    @pytest.fixture(scope="class")
    def article(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        return page.split('<article class="doc home">', 1)[1].split("</article>", 1)[0]

    def test_the_article_shows_the_ten_cards_of_getting_started(self, article):
        assert article.count('class="home-card"') == 10

    def test_no_other_track_is_listed_as_a_card(self, article):
        slugs = {p.slug for p in docs_source.pages_of(docs_source.read_tracks(DOCS)[0])}
        hrefs = set(re.findall(r'class="home-card" href="([^"]+)"', article))
        assert hrefs == {f"{slug}/" for slug in slugs}

    def test_the_menu_still_reaches_every_page(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert 'href="guides/actions/"' in page

    def test_a_card_holds_a_picture_and_a_line(self, article):
        card = article.split('class="home-card"', 1)[1].split("</a>", 1)[0]
        assert "<svg" in card and 'class="home-card-text"' in card

    def test_the_outline_lists_the_groups(self, out):
        page = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert '<a href="#first-steps">First steps</a>' in page


class TestRedirects:
    """DOC-22: an address a reader bookmarked keeps working, and names the page that replaced it."""

    @pytest.mark.parametrize(("old", "new"), sorted(docs_source.REDIRECTS.items()))
    def test_an_old_address_reaches_the_page_that_replaced_it(self, out, old, new):
        page = (out / "docs" / old / "index.html").read_text(encoding="utf-8")
        href = re.search(r'http-equiv="refresh" content="0; url=([^"]+)"', page)[1]
        target = (out / "docs" / old / href).resolve()
        assert target == (out / "docs" / new).resolve()
        assert (target / "index.html").is_file()

    @pytest.mark.parametrize(("old", "new"), sorted(docs_source.REDIRECTS.items()))
    def test_an_old_address_names_the_one_address_of_the_new_page(self, out, old, new):
        page = (out / "docs" / old / "index.html").read_text(encoding="utf-8")
        canonical = seo.canonical(seo.DEFAULT_SITE_URL, new)
        assert f'<link rel="canonical" href="{canonical}">' in page

    def test_a_redirect_never_overwrites_a_page_of_the_menu(self):
        listed = {
            page.slug
            for track in docs_source.read_tracks(DOCS)
            for page in docs_source.pages_of(track)
        }
        assert set(docs_source.REDIRECTS) & listed == set()

    def test_an_old_address_is_not_in_the_search_index(self, out):
        index = json.loads((out / "search-index.json").read_text(encoding="utf-8"))
        urls = {entry["url"] for entry in index}
        assert [f"docs/{slug}/" for slug in docs_source.REDIRECTS if f"docs/{slug}/" in urls] == []


class TestLinks:
    @staticmethod
    def _internal(html: str) -> list[str]:
        links = re.findall(r'(?:href|src)="([^"]+)"', html)
        return [x for x in links if not re.match(r"([a-z]+:|#|mailto)", x)]

    def test_every_relative_link_resolves_to_a_file(self, out):
        broken = []
        for page in _pages(out):
            for href in self._internal(page.read_text(encoding="utf-8")):
                target = (page.parent / href.split("#")[0].split("?")[0]).resolve()
                if target.is_dir():
                    target /= "index.html"
                if not target.is_file():
                    broken.append(f"{page.relative_to(out)} -> {href}")
        assert broken == []

    def test_no_link_is_absolute_so_a_project_site_works(self, out):
        html = (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")
        assert not re.search(r'(?:href|src)="/(?!/)', html)


class TestPageContent:
    @pytest.fixture(scope="class")
    def html(self, out):
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_title_is_the_page_title(self, html):
        assert "<title>Actions - Nexy</title>" in html

    def test_the_menu_marks_the_current_page(self, html):
        assert re.search(r'<a [^>]*aria-current="page"[^>]*>Actions</a>', html)

    def test_the_outline_lists_the_headings(self, html):
        assert 'href="#the-action-cycle"' in html

    def test_the_pager_names_the_neighbours(self, html):
        assert 'class="pager"' in html

    def test_the_menu_heads_every_section(self, html):
        """The sections of the menu read like the Nexy site: one quiet heading per track."""
        labels = [track.label for track in docs_source.read_tracks(DOCS)]
        assert re.findall(r'<p class="side-section">([^<]+)</p>', html) == labels

    def test_the_menu_is_made_of_collapsible_sections(self, html):
        # Each section is a <details>: the one holding the current page is open, the
        # others are not, and opening one never closes another.
        routing = 'data-section="File-based" data-scope="fbr" data-router="fbr"'
        assert f'<details class="group" {routing}>' in html
        forms = 'data-section="Forms and data" data-scope="core" open'
        assert f'<details class="group" {forms}>' in html

    def test_a_section_lists_all_its_pages(self, html):
        section = html.split('data-section="File-based"', 1)[1].split("</details>", 1)[0]
        group = next(
            group
            for track in docs_source.read_tracks(DOCS)
            for group in track.groups
            if group.title == "File-based" and group.router == "fbr"
        )
        assert section.count("<li>") == len(group.pages)

    def test_a_section_carries_no_sentence(self, html):
        """The accordion holds its name and its pages: prose stays out of the menu (A11)."""
        assert 'class="group-note"' not in html
        assert 'class="page-summary"' not in html

    def test_a_menu_item_is_the_link_then_the_pill(self, html):
        """A menu item is the label alone; only a marked page adds a pill, on the same line."""
        block = html.split('data-section="Forms and data"', 1)[1].split("</ul>", 1)[0]
        items = re.findall(r"<li>.*?</li>", block)
        pattern = re.compile(
            r'<li><a href="[^"]+"(?: aria-current="page")?>[^<]+</a>'
            r'(?:<span class="badge-new">New</span>)?</li>'
        )
        assert items and all(pattern.fullmatch(item) for item in items)

    def test_the_menu_draws_no_description(self, tmp_path):
        """A11: a page's summary is data for other surfaces, never a second menu line."""
        page = docs_source.Page(
            "only", "Only", "Only", tmp_path / "only.md", summary="Read this page"
        )
        group = docs_source.Group("G", "", [page])
        track = docs_source.Track("t", "T", "", [group])
        menu = build.nav_html([track], "only")
        assert "<small" not in menu and "Read this page" not in menu

    def test_the_menu_filter_reads_the_label(self):
        """Filtering matches a page label only, whatever the item grows into later."""
        script = (build.HERE / "assets" / "site.js").read_text(encoding="utf-8")
        keep = next(line for line in script.splitlines() if "const keep =" in line)
        assert "querySelector" in keep and "item.textContent" not in keep

    def test_the_pill_sits_on_the_label_line(self):
        """A11: the menu row is a flex line; the pill rides on the label's line, never under it."""
        css = (build.HERE / "assets" / "style.css").read_text(encoding="utf-8")
        row = css.split(".side li {", 1)[1].split("}", 1)[0]
        pill = css.split(".side .badge-new {", 1)[1].split("}", 1)[0]
        assert "display: flex" in row and "flex: none" in pill

    def test_only_the_groups_scroll_under_the_menu_head(self, html):
        assert '<div class="side-scroll">' in html

    def test_the_menu_has_a_search_button(self, html):
        assert 'class="search-open"' in html

    def test_the_first_page_has_no_previous_link(self, out):
        html = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert 'rel="prev"' not in html

    def test_titles_are_escaped(self):
        assert build.escape('<b>"x"</b>') == "&lt;b&gt;&quot;x&quot;&lt;/b&gt;"


CONTINUE = '<a href="#" class="continue" hidden>Continue</a>'


class TestProgress:
    """DOC-26: the pages one browser has read, and the page it offers next.

    The served HTML holds no reading state at all: a hidden link and the scripts that fill it.
    """

    @staticmethod
    def _button(html: str) -> str:
        """The button as it is served: a hidden link, and the same one on every page."""
        found = re.search(r'<a href="[^"]*" class="continue"[^>]*>[^<]*</a>', html)
        assert found is not None
        return found[0]

    @staticmethod
    def _menu(html: str) -> str:
        """The nav element of a page: the menu, nothing of what follows it."""
        return html.split('<nav class="side"', 1)[1].split("</nav>", 1)[0]

    @pytest.fixture(scope="class")
    def html(self, out):
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_button_is_a_hidden_link(self, html):
        assert CONTINUE in html

    def test_every_page_serves_the_same_button(self, out):
        """Nothing of the reading state is baked: one same button on every page that has a menu."""
        served = [page.read_text(encoding="utf-8") for page in _pages(out)]
        with_menu = [text for text in served if '<nav class="side"' in text]
        assert len(with_menu) > 1
        assert {self._button(text) for text in with_menu} == {CONTINUE}

    def test_the_menu_itself_holds_no_read_state(self, html):
        assert "seen" not in self._menu(html)

    def test_the_pager_is_left_alone(self, html):
        assert 'class="pager"' in html and 'rel="next"' in html

    def test_the_list_is_read_before_the_menu_paints(self, html):
        assert 'localStorage.getItem("nexy-docs-seen")' in html.split("</head>", 1)[0]

    def test_the_links_are_dimmed_while_the_menu_is_still_parsed(self, html):
        """Marked after the nav and before the panel: the reader never sees the plain link."""
        marking = html.index('classList.add("seen")')
        assert html.index("</nav>") < marking < html.index('<div class="panel"')

    def test_the_seen_key_follows_the_localstorage_patron(self):
        """One-line try/catch, like nexy-docs-theme, nexy-docs-side and nexy-docs-router."""
        script = (build.HERE / "assets" / "site.js").read_text(encoding="utf-8")
        written = next(line for line in script.splitlines() if "setItem('nexy-docs-seen'" in line)
        assert written.strip().startswith("try {") and "} catch {}" in written

    def test_the_button_offers_the_first_unread_page_of_the_menu(self):
        """One pass over the menu in served order, the last page read when none is left."""
        script = (build.HERE / "assets" / "site.js").read_text(encoding="utf-8")
        assert "!read.includes(slugOf(a.pathname))" in script
        assert "slugOf(a.pathname) === read.at(-1)" in script

    def test_a_read_page_is_only_dimmed(self):
        css = (build.HERE / "assets" / "style.css").read_text(encoding="utf-8")
        rule = css.split(".side a.seen", 1)[1].split("}", 1)[0]
        assert "color: var(--faint)" in rule and "content" not in rule

    def test_the_dimming_lets_hover_and_the_current_page_win(self):
        """The rules that lift a link come after it: order is the whole specificity mechanism."""
        css = (build.HERE / "assets" / "style.css").read_text(encoding="utf-8")
        assert (
            css.index(".side a.seen")
            < css.index(".side a:hover")
            < css.index('.side a[aria-current="page"]')
        )

    def test_the_dimmed_colour_exists_in_both_themes(self):
        css = (build.HERE / "assets" / "style.css").read_text(encoding="utf-8")
        light = css.split(":root {", 1)[1].split("}", 1)[0]
        dark = css.split(':root[data-theme="dark"] {', 1)[1].split("}", 1)[0]
        assert "--faint:" in light and "--faint:" in dark


class TestNewBadge:
    """DOC-27: one `{new}` token in a row of docs/README.md paints one pill in the menu."""

    PILL = '<a href="[^"]*"(?: aria-current="page")?>Page</a><span class="badge-new">New</span>'
    ROW = "| [Page](only.md) | Read this page {new} |"

    @staticmethod
    def _docs(root: Path, row: str) -> Path:
        root.mkdir(parents=True, exist_ok=True)
        (root / "only.md").write_text("# Only", encoding="utf-8")
        (root / "README.md").write_text(
            f"# Docs\n\n## Guides\n\n### Forms\n| Page | What you will do |\n|---|---|\n{row}\n",
            encoding="utf-8",
        )
        return root

    def test_a_marked_row_paints_the_pill_after_the_link(self, tmp_path):
        menu = build.nav_html(docs_source.read_tracks(self._docs(tmp_path, self.ROW)), "only")
        assert re.search(self.PILL, menu)

    def test_the_pill_is_labelled_new_and_the_token_is_not_drawn(self, tmp_path):
        menu = build.nav_html(docs_source.read_tracks(self._docs(tmp_path, self.ROW)), "only")
        assert menu.count(">New<") == 1 and "{new}" not in menu

    @staticmethod
    def _page_item(marked: bool) -> str:
        """The menu item of the one page of this site, exactly as the menu serves it."""
        pill = '<span class="badge-new">New</span>' if marked else ""
        return f'<li><a href="only/">Page</a>{pill}</li>'

    def test_an_unmarked_menu_is_the_menu_of_today(self, tmp_path):
        """Zero regression (F1): no token, no pill - the item is the label alone."""
        plain = self._docs(tmp_path / "a", "| [Page](only.md) | Read this page |")
        out = tmp_path / "out"
        build.build(out, plain)
        served = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert self._page_item(marked=False) in served
        assert "badge-new" not in served

    def test_a_marked_menu_adds_the_pill_and_nothing_else(self, tmp_path):
        """The one difference a token makes in the served bytes: the pill, and only it."""
        plain = self._docs(tmp_path / "a", "| [Page](only.md) | Read this page |")
        marked = self._docs(tmp_path / "b", self.ROW)
        before, after = tmp_path / "before", tmp_path / "after"
        build.build(before, plain)
        build.build(after, marked)
        first, second = _served_html(before), _served_html(after)
        assert set(first) == set(second)
        changed = [name for name in first if first[name] != second[name] and _english(name)]
        assert changed == ["docs/index.html", "docs/only/index.html"]
        assert self._page_item(marked=True) in second["docs/index.html"]
        assert self._page_item(marked=False) not in second["docs/index.html"]
        assert "{new}" not in second["docs/index.html"]

    def test_the_site_of_the_repo_paints_the_badges_of_its_menu(self, out):
        marked = [
            page
            for track in docs_source.read_tracks(DOCS)
            for page in docs_source.pages_of(track)
            if page.badge
        ]
        assert marked, "docs/README.md marks no page: the pill would go untested"
        menu = (out / "docs" / "index.html").read_text(encoding="utf-8")
        for page in marked:
            pattern = (
                rf'<a href="{re.escape(build.relative("", page.slug))}"[^>]*>'
                rf"{re.escape(page.label)}</a><span class=\"badge-new\">New</span>"
            )
            assert re.search(pattern, menu), page.slug

    def test_the_token_is_in_no_html_the_site_renders(self, out):
        stray = [
            page.relative_to(out).as_posix()
            for page in _pages(out)
            if "{new}" in page.read_text(encoding="utf-8")
        ]
        assert stray == []


class TestUsability:
    @pytest.fixture(scope="class")
    def html(self, out):
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_keyboard_can_skip_the_menu(self, html):
        assert 'class="skip" href="#content"' in html and 'id="content"' in html

    def test_the_page_says_which_colour_the_browser_bar_takes(self, html):
        assert 'name="theme-color"' in html

    def test_code_is_coloured_without_javascript(self, html):
        assert 'class="tok-' in html

    def test_a_wrong_address_gets_a_page_that_still_has_its_style(self, tmp_path):
        build.build(tmp_path, base="/nexy")
        page = (tmp_path / "404.html").read_text(encoding="utf-8")
        assert 'href="/nexy/assets/style.css"' in page and 'href="/nexy/docs/"' in page

    def test_the_base_may_be_empty_for_a_site_at_the_root_of_a_domain(self, tmp_path):
        build.build(tmp_path, base="")
        assert 'href="/assets/style.css"' in (tmp_path / "404.html").read_text(encoding="utf-8")

    def test_the_base_is_normalised(self):
        assert [build.base_of(x) for x in ("", "/", "nexy", "/nexy", "/nexy/")] == [
            "/",
            "/",
            "/nexy/",
            "/nexy/",
            "/nexy/",
        ]


class TestSearch:
    @pytest.fixture(scope="class")
    def index(self, out):
        return json.loads((out / "search-index.json").read_text(encoding="utf-8"))

    def test_every_page_is_searchable(self, out, index):
        assert len(index) == len(_pages(out))

    def test_an_entry_says_where_it_is(self, index):
        entry = next(e for e in index if e["title"] == "Actions")
        assert entry["url"] == "docs/guides/actions/"

    def test_an_entry_carries_text_but_no_markup(self, index):
        assert all("<" not in e["text"] for e in index)


class TestCrawlers:
    """What Google reads before a reader does: the sitemap, robots, the head of each page."""

    @pytest.fixture(scope="class")
    def page(self, out) -> str:
        return (out / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")

    def test_the_sitemap_lists_every_page_once(self, out):
        listed = (out / "sitemap.xml").read_text(encoding="utf-8").count("<url>")
        assert listed == _published(DOCS)

    def test_the_sitemap_names_the_published_address_of_a_page(self):
        xml = seo.sitemap([seo.canonical(seo.DEFAULT_SITE_URL, "guides/actions")])
        assert f"<loc>{seo.DEFAULT_SITE_URL}/docs/guides/actions/</loc>" in xml

    def test_robots_points_at_the_sitemap(self, out):
        robots = (out / "robots.txt").read_text(encoding="utf-8")
        assert f"Sitemap: {seo.DEFAULT_SITE_URL}/sitemap.xml" in robots

    def test_a_page_declares_one_canonical_address(self, page):
        assert page.count('rel="canonical"') == 1
        assert f'<link rel="canonical" href="{seo.DEFAULT_SITE_URL}/docs/guides/actions/">' in page

    def test_a_page_says_what_it_is_about(self, page):
        assert re.search(r'<meta name="description" content="[^"]{20,}">', page)

    def test_a_page_reads_as_a_card(self, page):
        assert '<meta property="og:title" content="Actions">' in page
        assert 'property="og:image"' in page and 'name="twitter:card"' in page

    def test_the_card_picture_ships_with_the_site(self, out):
        assert (out / "assets" / "og.png").is_file()

    def test_the_home_page_says_it_is_a_website(self, out):
        home = (out / "docs" / "index.html").read_text(encoding="utf-8")
        assert 'property="og:type" content="website"' in home

    def test_the_site_url_given_at_build_time_is_the_one_published(self, tmp_path):
        build.build(tmp_path, site_url="https://example.test/nexy")
        page = (tmp_path / "docs" / "guides" / "actions" / "index.html").read_text(encoding="utf-8")
        assert 'href="https://example.test/nexy/docs/guides/actions/"' in page

    def test_the_root_sends_the_crawler_to_the_docs(self, out):
        root = (out / "index.html").read_text(encoding="utf-8")
        assert f'href="{seo.home(seo.DEFAULT_SITE_URL)}"' in root


class TestLanguages:
    """Each language is a tree of its own under /docs/<code>/, served in that language."""

    @staticmethod
    def _page(out: Path, address: str) -> str:
        return (out / "docs" / address / "index.html").read_text(encoding="utf-8")

    def test_a_translated_page_is_served_in_its_language(self, out):
        assert '<html lang="fr" dir="ltr"' in self._page(out, "fr/guides/actions")

    def test_an_arabic_page_reads_right_to_left(self, out):
        assert '<html lang="ar" dir="rtl"' in self._page(out, "ar/guides/actions")

    def test_the_words_of_the_site_follow_the_language(self, out):
        assert '<span data-i18n="search">Rechercher</span>' in self._page(out, "fr/guides/actions")

    def test_the_picker_links_to_the_same_page_in_english(self, out):
        assert 'href="../../../guides/actions/" data-lang="en"' in self._page(
            out, "fr/guides/actions"
        )

    def test_the_menu_stays_in_the_language(self, out):
        assert 'href="../../getting-started/quick-start/"' in self._page(out, "fr/guides/actions")

    def test_a_page_names_its_translations_for_crawlers(self, out):
        assert 'hreflang="de" href=' in self._page(out, "fr/guides/actions")

    def test_each_language_searches_its_own_pages(self, out):
        index = json.loads((out / "search-index.fr.json").read_text(encoding="utf-8"))
        assert all(entry["url"].startswith("docs/fr") for entry in index)

    def test_a_page_says_which_index_it_searches(self, out):
        assert 'data-search="../../../../search-index.fr.json"' in self._page(
            out, "fr/guides/actions"
        )

    def test_the_edit_link_opens_the_english_source(self, out):
        assert "edit/main/docs/guides/actions.md" in self._page(out, "fr/guides/actions")

    def test_the_root_opens_the_language_of_the_reader(self, out):
        assert "nexy-docs-lang" in (out / "index.html").read_text(encoding="utf-8")


class TestUntranslatedPage:
    """A page with no translation yet is served in English under the language, and says so."""

    @pytest.fixture(scope="class")
    def page(self, tmp_path_factory: pytest.TempPathFactory) -> str:
        docs = tmp_path_factory.mktemp("docs")
        (docs / "README.md").write_text(
            "# Docs\n\n## Guides\n\n### Forms\n| Page | Summary |\n|---|---|\n"
            "| [Only](only.md) | Read this page |\n",
            encoding="utf-8",
        )
        (docs / "only.md").write_text("# Only\n\nThe text.\n", encoding="utf-8")
        out = tmp_path_factory.mktemp("site")
        build.build(out, docs)
        return (out / "docs" / "fr" / "only" / "index.html").read_text(encoding="utf-8")

    def test_it_says_it_is_still_in_english(self, page):
        assert 'class="lang-note"' in page and "encore en anglais" in page

    def test_its_canonical_is_the_english_page(self, page):
        assert f'rel="canonical" href="{seo.DEFAULT_SITE_URL}/docs/only/"' in page

    def test_it_claims_no_translation(self, page):
        assert 'rel="alternate" hreflang="fr"' not in page
