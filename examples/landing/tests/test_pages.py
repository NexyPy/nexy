def test_an_unknown_address_answers_404(client):
    assert client.get("/no-such-page").status_code == 404


def test_the_changelog_names_its_tab_after_its_heading(client):
    assert "<title>Changelog | Beacon</title>" in client.get("/changelog").text
