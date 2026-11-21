def test_an_unknown_address_answers_404(client):
    assert client.get("/no-such-page").status_code == 404
