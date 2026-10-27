"""Validation failures answer 422 with FastAPI's body; bad path params are a 404."""

from fastapi import FastAPI, Header
from fastapi.testclient import TestClient

from nexy.modules.routers.error_handlers import register_validation_error_handler


def _client() -> TestClient:
    app = FastAPI()
    register_validation_error_handler(app)

    @app.get("/items/{item_id}")
    async def item(item_id: int) -> dict:
        return {"id": item_id}

    @app.get("/secure")
    async def secure(x_token: str = Header(...)) -> dict:  # noqa: ARG001
        return {"ok": True}

    @app.post("/body")
    async def body(payload: dict) -> dict:
        return payload

    return TestClient(app, raise_server_exceptions=False)


class TestValidationErrors:
    def test_missing_header_is_422_with_details(self):
        response = _client().get("/secure")
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail[0]["loc"] == ["header", "x-token"]

    def test_invalid_body_is_422(self):
        response = _client().post("/body", content="not json")
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_bad_path_param_is_a_404_page(self):
        assert _client().get("/items/abc").status_code == 404

    def test_valid_request_passes(self):
        assert _client().get("/items/7").json() == {"id": 7}


class TestHttpExceptions:
    @staticmethod
    def _client() -> TestClient:
        from starlette.exceptions import HTTPException

        from nexy.modules.routers.error_handlers import handle_http_exception

        app = FastAPI()
        app.add_exception_handler(HTTPException, handle_http_exception)

        @app.get("/forbidden")
        async def forbidden() -> dict:
            raise HTTPException(status_code=403, detail="No <b>access</b> for Ada")

        @app.get("/missing")
        async def missing() -> dict:
            raise HTTPException(status_code=404, detail="gone")

        return TestClient(app, raise_server_exceptions=False)

    def test_browser_gets_an_escaped_html_page(self):
        response = self._client().get("/forbidden", headers={"accept": "text/html"})
        assert response.status_code == 403
        assert response.headers["content-type"].startswith("text/html")
        assert "<b>access</b>" not in response.text
        assert "&lt;b&gt;access&lt;/b&gt;" in response.text

    def test_api_client_gets_json(self):
        response = self._client().get("/forbidden", headers={"accept": "application/json"})
        assert response.status_code == 403
        assert response.json() == {"detail": "No <b>access</b> for Ada"}

    def test_404_is_a_typed_html_page_for_browsers(self):
        response = self._client().get("/missing", headers={"accept": "text/html"})
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("text/html")

    def test_404_is_json_for_api_clients(self):
        response = self._client().get("/missing", headers={"accept": "application/json"})
        assert response.json() == {"detail": "gone"}

    def test_a_browser_that_also_accepts_json_still_gets_the_page(self):
        response = self._client().get(
            "/missing", headers={"accept": "text/html,application/json;q=0.9"}
        )
        assert response.headers["content-type"].startswith("text/html")


class TestPathParamNegotiation:
    def test_bad_path_param_is_json_for_api_clients(self):
        response = _client().get("/items/abc", headers={"accept": "application/json"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}

    def test_bad_path_param_is_html_for_browsers(self):
        response = _client().get("/items/abc", headers={"accept": "text/html"})
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("text/html")
