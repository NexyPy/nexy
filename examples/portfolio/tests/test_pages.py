import re

from src.content.work import PROJECTS


def test_the_home_page_shows_the_featured_projects(client):
    assert "Halden Rail" in client.get("/").text
