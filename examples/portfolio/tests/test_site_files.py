def test_the_sitemap_lists_the_work_page(client):
    assert "<loc>https://noor.example/work</loc>" in client.get("/sitemap.xml").text


def test_robots_points_to_the_sitemap(client):
    assert "Sitemap: https://noor.example/sitemap.xml" in client.get("/robots.txt").text
