from src.docs.search import ENTRIES, search


def test_a_word_finds_the_section_that_has_it():
    assert "Change the passphrase" in [hit.heading for hit in search("passphrase")]


def test_every_word_of_the_query_must_be_there():
    assert search("prune systemd") == []


def test_a_word_in_a_title_comes_first():
    assert search("restore")[0].title == "cairn restore"


def test_the_case_does_not_matter():
    assert search("SYSTEMD") == search("systemd")


def test_an_empty_query_finds_nothing():
    assert search("   ") == []


def test_the_results_are_limited():
    assert len(search("the", limit=5)) == 5


def test_a_result_links_to_its_heading():
    assert search("launchd")[0].url == "/docs/guides/schedule#macos"


def test_the_snippet_shows_the_word_found():
    assert "launchd" in search("launchd")[0].snippet


def test_the_snippet_has_no_markdown_left():
    assert "`" not in search("dry-run")[0].snippet


def test_every_page_has_an_entry_for_its_top():
    assert len({entry.url.split("#")[0] for entry in ENTRIES}) == 11


def test_the_snippet_starts_on_a_whole_word():
    hit = search("renaming")[0]
    start = hit.snippet.removeprefix("...").removesuffix("...")
    assert hit.text[hit.text.find(start) - 1] == " "
