"""The About page: Markdown in a folder that gives it a layout for reading."""


def test_the_about_page_is_read_from_markdown(client):
    assert '<h1 id="about-plain-text">About Plain Text</h1>' in client.get("/about").text


def test_the_sitemap_lists_the_about_page(client):
    assert "<loc>https://plaintext.example/about</loc>" in client.get("/sitemap.xml").text
