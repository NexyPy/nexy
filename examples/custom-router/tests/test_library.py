from conftest import STAFF

JSON = {"Accept": "application/json"}


def test_a_route_of_the_fastapi_service_answers(client):
    assert len(client.get("/api/v1/books").json()) == 3


def test_a_path_value_of_the_wrong_type_answers_404_not_422(client):
    assert client.get("/api/v1/books/one", headers=JSON).status_code == 404


def test_an_api_client_gets_the_error_detail_as_json(client):
    assert client.get("/api/v1/books/99", headers=JSON).json() == {"detail": "No such book."}


def test_a_browser_gets_the_404_page(client):
    response = client.get("/api/v1/books/99", headers={"Accept": "text/html"})
    assert response.headers["content-type"].startswith("text/html")


def test_the_dependency_of_the_service_still_guards_its_routes(client):
    assert client.post("/api/v1/books/1/loan").status_code == 401


def test_staff_lends_a_book(client):
    assert client.post("/api/v1/books/1/loan", headers=STAFF).json()["on_loan"] is True


def test_a_book_on_loan_cannot_be_lent_twice(client):
    assert client.post("/api/v1/books/2/loan", headers=STAFF).status_code == 409


def test_the_moved_route_answers_from_its_file(client):
    assert [book["id"] for book in client.get("/api/v2/books").json()] == [1, 3]


def test_the_page_reads_the_same_books(client):
    client.post("/api/v1/books/3/loan", headers=STAFF)
    assert client.get("/").text.count("On loan") == 2


def test_the_page_is_a_whole_document(client):
    assert client.get("/").text.lstrip().startswith("<!DOCTYPE html>")
