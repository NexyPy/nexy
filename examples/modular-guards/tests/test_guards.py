import pytest
from conftest import EDITOR, WRITER

NEW = {"title": "Ferry timetable", "body": "Winter hours start in October."}


def test_anyone_reads_the_published_stories(client):
    assert [story["slug"] for story in client.get("/api/stories/").json()] == ["harbour-reopens"]


def test_a_draft_is_hidden_from_the_public(client):
    assert client.get("/api/stories/bridge-vote/").status_code == 404


@pytest.mark.parametrize("headers", [{}, {"X-Api-Key": "guess"}, {"X-Api-Key": ""}])
def test_drafts_need_a_known_key(client, headers):
    assert client.get("/api/drafts/", headers=headers).status_code == 401


def test_a_writer_reads_the_drafts(client):
    assert client.get("/api/drafts/", headers=WRITER).json()[0]["slug"] == "bridge-vote"


def test_a_writer_adds_a_draft(client):
    assert client.post("/api/drafts/", json=NEW, headers=WRITER).status_code == 201


def test_the_same_title_twice_is_refused(client):
    client.post("/api/drafts/", json=NEW, headers=WRITER)
    assert client.post("/api/drafts/", json=NEW, headers=WRITER).status_code == 409


def test_an_empty_title_is_refused(client):
    response = client.post("/api/drafts/", json={"title": "", "body": "x"}, headers=WRITER)
    assert response.status_code == 422


def test_a_writer_cannot_publish(client):
    assert client.post("/api/drafts/bridge-vote/publish/", headers=WRITER).status_code == 403


def test_publishing_without_a_key_is_refused_before_the_role(client):
    assert client.post("/api/drafts/bridge-vote/publish/").status_code == 401


def test_an_editor_publishes(client):
    client.post("/api/drafts/bridge-vote/publish/", headers=EDITOR)
    assert client.get("/api/stories/bridge-vote/").status_code == 200


def test_reading_a_story_stays_public_next_to_a_guarded_delete(client):
    assert client.get("/api/stories/harbour-reopens/").status_code == 200


def test_a_writer_cannot_delete(client):
    assert client.delete("/api/stories/harbour-reopens/", headers=WRITER).status_code == 403


def test_an_editor_deletes(client):
    assert client.delete("/api/stories/harbour-reopens/", headers=EDITOR).status_code == 204


def test_the_home_page_lists_the_published_stories(client):
    assert "The harbour reopens" in client.get("/").text
