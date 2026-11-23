import pytest
from conftest import add_address

from src.services import bookmarks


def add(client, title, url):
    return client.post(add_address(client), data={"title": title, "url": url})


def test_a_bookmark_added_from_the_form_is_listed(client):
    add(client, "Nexy docs", "https://github.com/NexyPy/nexy")
    assert "Nexy docs" in client.get("/").text


def test_adding_lands_back_on_the_list(client):
    assert add(client, "Nexy docs", "https://example.com").headers["location"] == "/?added=1"


def test_the_search_ignores_case(client):
    bookmarks.add("PostgreSQL manual", "https://www.postgresql.org/docs/")
    assert [b.title for b in bookmarks.search("postgresql")] == ["PostgreSQL manual"]


def test_a_percent_sign_is_searched_as_itself(client):
    bookmarks.add("Ten percent", "https://example.com/a")
    bookmarks.add("100% sure", "https://example.com/b")
    assert [b.title for b in bookmarks.search("%")] == ["100% sure"]


def test_the_newest_comes_first(client):
    bookmarks.add("First", "https://example.com/1")
    bookmarks.add("Second", "https://example.com/2")
    assert [b.title for b in bookmarks.search()] == ["Second", "First"]


@pytest.mark.parametrize("url", ["javascript:alert(1)", "ftp://example.com", "example.com", ""])
def test_an_address_that_is_not_a_web_page_is_refused(client, url):
    assert "error=url" in add(client, "Bad", url).headers["location"]


def test_a_refused_bookmark_is_not_saved(client):
    add(client, "Bad", "javascript:alert(1)")
    assert bookmarks.search() == []


def test_an_empty_title_is_refused(client):
    assert "error=title" in add(client, "  ", "https://example.com").headers["location"]


def test_a_title_is_printed_as_text(client):
    bookmarks.add("<script>alert(1)</script>", "https://example.com")
    assert "<script>alert(1)" not in client.get("/").text


def test_the_page_names_the_database_it_uses(client):
    from src.configs.db import engine

    assert f"<strong>{engine.dialect.name}</strong>" in client.get("/").text
