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


def test_a_case_study_names_its_tab(client):
    assert "<title>Tidepool | Noor Halvorsen</title>" in client.get("/work/tidepool").text


def test_a_case_study_links_every_picture_for_the_lightbox(client):
    assert client.get("/work/grove").text.count("data-lightbox") == 3


def test_a_case_study_links_to_the_next_one(client):
    assert 'href="/work/grove" class="group mt-24' in client.get("/work/tidepool").text


def test_an_unknown_case_study_answers_404(client):
    assert client.get("/work/nothing-here").status_code == 404


def test_the_about_page_names_its_tab(client):
    assert "<title>About | Noor Halvorsen</title>" in client.get("/about").text


def test_an_unknown_address_answers_404(client):
    assert client.get("/no-such-page").status_code == 404
