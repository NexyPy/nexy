from src.services.waitlist import MESSAGES


def test_the_home_page_shows_the_outcome_the_form_came_back_with(client):
    assert MESSAGES["invalid"] in client.get("/?waitlist=invalid").text


def test_the_home_page_ignores_an_unknown_outcome(client):
    assert 'role="status"' not in client.get("/?waitlist=<script>").text


def test_the_changelog_names_its_tab_after_its_heading(client):
    assert "<title>Changelog | Beacon</title>" in client.get("/changelog").text


def test_an_unknown_address_answers_404(client):
    assert client.get("/no-such-page").status_code == 404
