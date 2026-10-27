"""@UseRoute metadata reaches the OpenAPI schema, and guards reject calls."""

from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

from nexy.decorators import Controller, Module, UseGuard, UseResponse, UseRoute


def _require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/docs-demo")
class DocumentedController:
    @UseRoute(
        name="list_things",
        tags=["things"],
        summary="List things",
        description="Every thing, newest first.",
        deprecated=True,
        operation_id="listThings",
        openapi_extra={"x-audience": "internal"},
    )
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []


@Controller(prefix="/hidden")
class HiddenController:
    @UseRoute(include_in_schema=False)
    async def get(self) -> dict:
        return {"ok": True}


@Controller(prefix="/guarded")
@UseGuard(_require_token)
class GuardedController:
    async def get(self) -> dict:
        return {"ok": True}


@Module()
class DemoModule:
    controllers = [DocumentedController, HiddenController, GuardedController]


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(DemoModule)
    return TestClient(app, raise_server_exceptions=False)


class TestRouteMetadata:
    def _operation(self):
        spec = _client().get("/openapi.json").json()
        return spec["paths"]["/docs-demo/"]["get"]

    def test_summary_and_description_are_published(self):
        operation = self._operation()
        assert operation["summary"] == "List things"
        assert operation["description"] == "Every thing, newest first."

    def test_deprecated_operation_id_and_extra_are_published(self):
        operation = self._operation()
        assert operation["deprecated"] is True
        assert operation["operationId"] == "listThings"
        assert operation["x-audience"] == "internal"

    def test_hidden_route_is_not_in_the_schema_but_still_served(self):
        client = _client()
        assert "/hidden/" not in client.get("/openapi.json").json()["paths"]
        assert client.get("/hidden/").status_code == 200


class TestGuards:
    def test_guard_rejects_a_bad_token(self):
        assert _client().get("/guarded/", headers={"x-token": "nope"}).status_code == 403

    def test_guard_accepts_the_right_token(self):
        assert _client().get("/guarded/", headers={"x-token": "secret"}).status_code == 200
