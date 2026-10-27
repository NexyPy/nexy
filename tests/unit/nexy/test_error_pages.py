"""The pages Nexy shows when nothing else answers: calm, readable, safe."""

from __future__ import annotations

import re

import pytest

from nexy.errors import InternalServerError, NotFound, error_page


def _body(response) -> str:
    return response.body.decode("utf-8")


class TestStatusPages:
    def test_not_found_is_a_404_document(self):
        response = NotFound()
        assert response.status_code == 404
        assert _body(response).lstrip().lower().startswith("<!doctype html>")

    def test_internal_error_is_a_500_document(self):
        response = InternalServerError()
        assert response.status_code == 500
        assert _body(response).lstrip().lower().startswith("<!doctype html>")

    def test_the_page_names_its_status_and_offers_a_way_home(self):
        body = _body(NotFound())
        assert "404" in body and "Page not found" in body and 'href="/"' in body

    def test_the_page_never_uses_the_old_yellow_and_red(self):
        body = _body(NotFound()).lower()
        assert "yellow" not in body and "background-color:red" not in body


class TestGenericPage:
    @pytest.mark.parametrize(("code", "title"), [(401, "Unauthorized"), (403, "Forbidden")])
    def test_any_status_gets_a_page(self, code, title):
        response = error_page(code, title, "You cannot see this.")
        assert response.status_code == code
        assert title in _body(response) and "You cannot see this." in _body(response)

    def test_the_message_is_escaped(self):
        body = _body(error_page(400, "Bad request", "<script>alert(1)</script>"))
        assert "<script>alert(1)</script>" not in body
        assert "&lt;script&gt;" in body

    def test_the_title_is_escaped(self):
        assert "<img" not in _body(error_page(400, "<img src=x>", "m"))


class TestDocument:
    def test_it_adapts_to_a_dark_system_theme(self):
        assert "prefers-color-scheme: dark" in _body(NotFound())

    def test_it_is_self_contained(self):
        # Shown when the app is broken: no external font, script or stylesheet.
        body = _body(NotFound())
        assert not re.search(r'(src|href)="https?://', body)
        assert "<script" not in body

    def test_it_declares_the_language_and_viewport(self):
        body = _body(NotFound())
        assert '<html lang="en"' in body and 'name="viewport"' in body
