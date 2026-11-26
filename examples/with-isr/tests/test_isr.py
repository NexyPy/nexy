import re
import time

import pytest

WINDOW = 30


def render(response):
    return int(re.search(r"<strong data-render>(\d+)</strong>", response.text).group(1))


@pytest.fixture
def clock(monkeypatch):
    """Moves time forward without waiting: the stores read time.time()."""
    start = time.time()
    offset = [0.0]
    monkeypatch.setattr(time, "time", lambda: start + offset[0])
    return offset


def test_the_cached_page_says_how_long_it_is_kept(client):
    expected = f"public, s-maxage={WINDOW}, stale-while-revalidate={WINDOW}"
    assert client.get("/").headers["cache-control"] == expected


def test_a_second_visit_is_not_rendered_again(client):
    first = render(client.get("/"))
    assert render(client.get("/")) == first


def test_the_live_page_is_rendered_on_every_visit(client):
    first = render(client.get("/live"))
    assert render(client.get("/live")) > first


def test_an_old_copy_is_still_sent_at_once(client, clock):
    first = render(client.get("/"))
    clock[0] = WINDOW + 1
    assert render(client.get("/")) == first


def test_the_old_copy_is_replaced_behind_it(client, clock):
    first = render(client.get("/"))
    clock[0] = WINDOW + 1
    client.get("/")  # sends the old copy, and starts the new render
    assert render(client.get("/")) > first
