import re

SITE = "https://crumb.example"


def listed(client):
    return set(re.findall(r"<loc>([^<]+)</loc>", client.get("/sitemap.xml").text))


def test_the_sitemap_lists_each_static_page(client):
    assert listed(client) == {f"{SITE}/", f"{SITE}/menu", f"{SITE}/visit"}


def test_the_sitemap_is_xml(client):
    assert client.get("/sitemap.xml").headers["content-type"].startswith("application/xml")


def test_a_dynamic_page_answers_but_is_not_listed(client):
    assert client.get("/menu/rye").status_code == 200


def test_robots_points_to_the_sitemap(client):
    assert f"Sitemap: {SITE}/sitemap.xml" in client.get("/robots.txt").text


def test_an_unknown_bake_answers_404(client):
    assert client.get("/menu/croissant").status_code == 404
