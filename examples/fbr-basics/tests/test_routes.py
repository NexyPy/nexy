import pytest


@pytest.mark.parametrize(
    ("address", "heading"),
    [
        ("/", "Six files, six addresses"),
        ("/about", "About"),
        ("/birds", "Birds"),
        ("/birds/robin", "European robin"),
    ],
)
def test_a_file_answers_its_address(client, address, heading):
    assert f">{heading}</h1>" in client.get(address).text


def test_a_nested_layout_wraps_its_folder(client):
    assert 'aria-label="Birds"' in client.get("/birds/wren").text


def test_a_nested_layout_stays_in_its_folder(client):
    assert 'aria-label="Birds"' not in client.get("/about").text


def test_an_unknown_bird_answers_404(client):
    assert client.get("/birds/dodo").status_code == 404


def test_a_python_route_answers_json(client):
    assert client.get("/api/birds").json()[0]["slug"] == "robin"


def test_an_address_with_no_file_answers_the_404_page(client):
    assert "No page here" in client.get("/no-such-page").text
