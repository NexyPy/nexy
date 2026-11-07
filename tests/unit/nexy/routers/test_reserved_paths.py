"""A route on the path of the API reference, or of its schema, is never served: say so (#81)."""

from __future__ import annotations

from fastapi import FastAPI

from nexy.modules.routers.reserved_paths import shadowed_routes


def _reference() -> str:
    return "reference"


def _app(*paths: str, source: str | None = None) -> FastAPI:
    app = FastAPI()
    app.get("/docs", include_in_schema=False)(_reference)
    for path in paths:

        def page() -> str:
            return "page"

        if source:
            page.__nexy_source__ = source  # type: ignore[attr-defined]
        app.get(path)(page)
    return app


def _shadowed(app: FastAPI) -> list[str]:
    return shadowed_routes(app.routes, "/docs", _reference)


def test_a_page_at_the_reference_path_is_reported():
    assert len(_shadowed(_app("/docs"))) == 1


def test_a_catch_all_under_the_reference_path_is_reported():
    # `/docs` would redirect to `/docs/`, which the catch-all answers: the reference answers first.
    assert len(_shadowed(_app("/docs/{slug:path}"))) == 1


def test_a_page_under_the_reference_path_is_not_reported():
    assert _shadowed(_app("/docs/intro")) == []


def test_a_page_at_the_schema_path_is_reported():
    assert len(_shadowed(_app("/openapi.json"))) == 1


def test_the_warning_names_the_route_file():
    line = _shadowed(_app("/docs", source="src/routes/docs.nexy"))[0]
    assert line.startswith("src/routes/docs.nexy is never served at /docs")


def test_the_warning_names_the_setting_to_change():
    assert "useDocsUrl" in _shadowed(_app("/docs"))[0]


def test_the_warning_names_the_path_when_the_file_is_unknown():
    assert _shadowed(_app("/openapi.json"))[0].startswith("GET /openapi.json is never served")


def test_without_the_reference_only_the_schema_path_is_checked():
    assert shadowed_routes(_app("/docs").routes, None, _reference) == []
