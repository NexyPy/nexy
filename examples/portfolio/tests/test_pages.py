import re

from src.content.work import PROJECTS


def test_the_home_page_shows_the_featured_projects(client):
    assert "Halden Rail" in client.get("/").text


def test_the_work_page_lists_every_project(client):
    page = client.get("/work").text
    assert all(f'href="/work/{project.slug}"' in page for project in PROJECTS)


def test_the_work_page_filters_by_discipline(client):
    assert 'href="/work/ember"' not in client.get("/work?discipline=research").text


def test_the_work_page_marks_the_chosen_filter(client):
    page = client.get("/work?discipline=brand").text
    assert re.search(r'href="/work\?discipline=brand"\s+aria-current="page"', page)


def test_an_unknown_discipline_says_so(client):
    assert "There is no discipline called" in client.get("/work?discipline=knitting").text


def test_an_unknown_discipline_is_escaped(client):
    page = client.get("/work?discipline=<b>bold</b>").text
    assert "&lt;b&gt;bold&lt;/b&gt;" in page
