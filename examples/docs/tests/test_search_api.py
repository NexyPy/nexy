def test_the_search_answers_json(client):
    assert client.get("/api/search?q=launchd").json()[0]["url"] == "/docs/guides/schedule#macos"


def test_an_empty_query_answers_an_empty_list(client):
    assert client.get("/api/search").json() == []


def test_a_query_longer_than_a_search_box_is_cut(client):
    assert client.get("/api/search?q=" + "a" * 10_000).status_code == 200
