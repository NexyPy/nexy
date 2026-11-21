import re

from src.chat import store


def send(client, **fields):
    form = {"room": "general", "name": "Ines", "text": "Hello"} | fields
    return client.post("/send", data=form)


def test_the_chat_opens_on_the_general_room(client):
    assert client.get("/").headers["location"] == "/rooms/general"


def test_a_room_shows_its_messages(client):
    assert "Stand-up moves to 10:30" in client.get("/rooms/general").text


def test_a_room_shows_only_its_own_messages(client):
    assert "Stand-up moves" not in client.get("/rooms/design").text


def test_the_current_room_is_marked(client):
    assert re.search(
        r'href="/rooms/design"[^>]*aria-current="page"', client.get("/rooms/design").text
    )


def test_a_room_that_does_not_exist_answers_404(client):
    assert client.get("/rooms/nowhere").status_code == 404


def test_the_form_sends_back_to_the_room(client):
    assert send(client).headers["location"] == "/rooms/general#send"


def test_the_form_stores_the_message(client):
    send(client, text="From the form")
    assert store.messages("general")[-1].text == "From the form"


def test_a_sent_name_is_remembered_in_a_cookie(client):
    send(client, name="Ines")
    assert 'value="Ines"' in client.get("/rooms/general").text


def test_a_refused_message_says_why_after_the_redirect(client):
    location = send(client, name="").headers["location"]
    assert store.NOTES["name"] in client.get(location).text


def test_a_note_key_that_does_not_exist_shows_nothing(client):
    page = client.get("/rooms/general?note=<b>made-up</b>").text
    assert "made-up" not in page


def test_a_message_is_printed_as_text(client):
    send(client, text="<script>alert(1)</script>")
    assert "<script>alert(1)" not in client.get("/rooms/general").text


def test_a_name_is_printed_as_text(client):
    send(client, name="<b>Ines</b>")
    assert "<b>Ines</b>" not in client.get("/rooms/general").text


def test_the_island_gets_the_messages_it_has_not_shown(client):
    last = store.messages("general")[-1].id
    answer = client.post(
        "/send",
        data={"room": "general", "name": "Ines", "text": "Live", "after": str(last)},
        headers={"accept": "application/json"},
    )
    assert [m["text"] for m in answer.json()["messages"]] == ["Live"]


def test_the_island_gets_the_note_of_a_refused_message(client):
    answer = client.post(
        "/send",
        data={"room": "general", "name": "", "text": "x"},
        headers={"accept": "application/json"},
    )
    assert answer.json()["note"] == store.NOTES["name"]


def test_new_messages_are_listed_after_an_id(client):
    last = store.messages("design")[-1].id
    store.send("design", "Ines", "Newer")
    answer = client.get(f"/api/messages?room=design&after={last}")
    assert [m["text"] for m in answer.json()] == ["Newer"]


def test_new_messages_of_an_unknown_room_are_refused(client):
    assert client.get("/api/messages?room=nowhere&after=0").status_code == 400


def test_an_id_too_large_for_sqlite_is_refused(client):
    assert client.get("/api/messages?room=general&after=" + "9" * 40).status_code == 400
