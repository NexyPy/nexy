from src.docs.nav import PAGES, SECTIONS, neighbours


def test_every_page_of_the_menu_has_a_markdown_file():
    assert all(page.file.is_file() for page in PAGES)


def test_every_markdown_file_is_in_the_menu():
    files = {path.resolve() for path in (PAGES[0].file.parent).rglob("*.md")}
    assert files == {page.file.resolve() for page in PAGES}


def test_the_menu_starts_with_the_introduction():
    assert SECTIONS[0].pages[0].url == "/docs"


def test_the_first_page_has_no_previous_page():
    assert neighbours("/docs")[0] is None


def test_the_last_page_has_no_next_page():
    assert neighbours(PAGES[-1].url)[1] is None


def test_a_page_in_the_middle_has_both_neighbours():
    before, after = neighbours("/docs/quick-start")
    assert (before.url, after.url) == ("/docs/installation", "/docs/configuration")


def test_an_address_outside_the_menu_has_no_neighbours():
    assert neighbours("/somewhere") == (None, None)
