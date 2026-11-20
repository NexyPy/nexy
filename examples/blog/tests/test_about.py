"""The About page: Markdown in a folder that gives it a layout for reading."""


def test_the_about_page_is_read_from_markdown(client):
    assert '<h1 id="about-plain-text">About Plain Text</h1>' in client.get("/about").text


def test_the_sitemap_lists_the_about_page(client):
    assert "<loc>https://plaintext.example/about</loc>" in client.get("/sitemap.xml").text


def test_a_markdown_page_names_the_tab_after_its_first_heading(client):
    assert "<title>About Plain Text | Plain Text</title>" in client.get("/about").text


def test_a_markdown_page_is_set_for_reading(client):
    assert 'class="nx-container blog-page blog-prose"' in client.get("/about").text
