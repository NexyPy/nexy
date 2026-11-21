import re


def test_the_root_sends_to_the_language_of_the_browser(client):
    response = client.get("/", headers={"accept-language": "fr-FR,fr;q=0.9"})
    assert response.headers["location"] == "/fr"


def test_the_root_sends_to_english_by_default(client):
    assert client.get("/", headers={"accept-language": "ja"}).headers["location"] == "/en"


def test_a_french_page_says_it_is_french(client):
    assert '<html lang="fr">' in client.get("/fr/about").text


def test_a_french_page_is_in_french(client):
    assert "Deux amis" in client.get("/fr/about").text


def test_the_switcher_links_the_same_page_in_each_language(client):
    html = client.get("/fr/about").text
    assert re.findall(r'<a href="([^"]+)" hreflang', html) == ["/en/about", "/fr/about"]


def test_the_page_lists_its_other_languages_for_search_engines(client):
    html = client.get("/en/about").text
    assert re.findall(r'hreflang="([^"]+)" href="([^"]+)"', html) == [
        ("en", "http://testserver/en/about"),
        ("fr", "http://testserver/fr/about"),
        ("x-default", "http://testserver/"),
    ]


def test_a_language_the_site_does_not_have_answers_404(client):
    assert client.get("/de/about").status_code == 404


def test_the_404_page_speaks_the_language_of_the_address(client):
    assert "Aucune page ici" in client.get("/fr/nothing/here").text


def test_html_in_the_address_is_printed_as_text(client):
    html = client.get('/fr/"><script>alert(1)</script>').text
    assert "<script>alert(1)" not in html
