import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.routing import Mount

from nexy.modules.routers.error_handlers import handle_http_exception
from nexy.modules.routers.hmr import setup_hmr
from nexy.modules.routers.static_assets import FAVICON_SVG, setup_favicon, setup_static_files


class TestStaticAssets:
    @pytest.mark.usefixtures("nexy_project")
    def test_favicon_falls_back_to_builtin_svg(self) -> None:
        server = FastAPI()
        setup_favicon(server, "src/routes")  # no favicon anywhere in tmp_path

        response = TestClient(server).get("/favicon.ico")

        assert response.status_code == 200
        assert response.content == FAVICON_SVG.encode("utf-8")
        assert response.headers["content-type"].startswith("image/x-icon")

    @pytest.mark.usefixtures("nexy_project")
    def test_favicon_prefers_router_folder(self, tmp_path) -> None:
        custom = b"custom-favicon-bytes"
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "routes").mkdir()
        (tmp_path / "src" / "routes" / "favicon.ico").write_bytes(custom)
        server = FastAPI()
        setup_favicon(server, "src/routes")

        response = TestClient(server).get("/favicon.ico")

        assert response.content == custom

    @pytest.mark.usefixtures("nexy_project")
    def test_static_files_mounts_existing_directories_only(self, tmp_path) -> None:
        server = FastAPI()
        (tmp_path / "public").mkdir()

        setup_static_files(server)

        mounts = [r.path for r in server.routes if isinstance(r, Mount)]
        assert "/public" in mounts
        assert "/assets" not in mounts  # __nexy__/client/assets does not exist


class TestErrorHandlers:
    def test_http_exception_maps_to_nexy_404_page(self) -> None:
        from starlette.exceptions import HTTPException

        response = handle_http_exception(
            _request=None,  # unused by the handler
            exc=HTTPException(status_code=404),
        )

        assert response.status_code == 404
        assert b"404" in response.body

    def test_http_exception_maps_to_nexy_500_page(self) -> None:
        from starlette.exceptions import HTTPException

        response = handle_http_exception(
            _request=None,
            exc=HTTPException(status_code=500),
        )

        assert response.status_code == 500
        assert b"500" in response.body

    def test_other_status_falls_back_to_plain_response(self) -> None:
        from starlette.exceptions import HTTPException

        response = handle_http_exception(
            _request=None,
            exc=HTTPException(status_code=403, detail="forbidden"),
        )

        assert response.status_code == 403


class TestHmrSetup:
    def test_registers_websocket_route(self) -> None:
        server = FastAPI()
        setup_hmr(server)

        routes = [r.path for r in server.routes]
        assert "/_nexy/hmr" in routes


class TestFaviconRouteContract:
    def test_favicon_route_hidden_from_openapi(self) -> None:
        server = FastAPI()
        setup_favicon(server, "src/routes")

        route = next(r for r in server.routes if getattr(r, "path", None) == "/favicon.ico")

        assert route.include_in_schema is False
