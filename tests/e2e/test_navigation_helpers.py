"""redirect, notFound, forbidden and unauthorized work in every place a request is handled."""

from __future__ import annotations

from pathlib import Path

from tests.e2e.project import request, scaffold, write

NO_HEADERS: dict[str, str] = {}
JSON = {"accept": "application/json"}


def _page(call: str) -> str:
    return f"---\nfrom nexy import {call.split('(')[0]}\n{call}\n---\n<p>never shown</p>\n"


def _web(tmp_path: Path, files: dict[str, str]) -> Path:
    scaffold(tmp_path, "web-fbr", "none")
    for name, text in files.items():
        write(tmp_path, name, text)
    return tmp_path


class TestInAPage:
    def test_a_redirect_answers_307_with_a_location_and_no_page(self, tmp_path):
        project = _web(tmp_path, {"src/routes/old.nexy": _page('redirect("/about")')})
        status, headers, body = request(project, ("/old", NO_HEADERS))[0]
        assert (status, headers["location"], body) == (307, "/about", "")

    def test_a_permanent_redirect_answers_308(self, tmp_path):
        project = _web(tmp_path, {"src/routes/old.nexy": _page('permanentRedirect("/about")')})
        assert request(project, ("/old", NO_HEADERS))[0][0] == 308

    def test_not_found_shows_the_404_page(self, tmp_path):
        project = _web(tmp_path, {"src/routes/gone.nexy": _page("notFound()")})
        status, _, body = request(project, ("/gone", {"accept": "text/html"}))[0]
        assert status == 404 and "<html" in body.lower()

    def test_not_found_is_json_for_an_api_client(self, tmp_path):
        project = _web(tmp_path, {"src/routes/gone.nexy": _page('notFound("No such post")')})
        status, headers, body = request(project, ("/gone", JSON))[0]
        assert (status, "No such post" in body) == (404, True)
        assert headers["content-type"].startswith("application/json")

    def test_forbidden_answers_403(self, tmp_path):
        project = _web(tmp_path, {"src/routes/vip.nexy": _page("forbidden()")})
        assert request(project, ("/vip", NO_HEADERS))[0][0] == 403


class TestInAnApiHandler:
    def test_a_handler_can_redirect(self, tmp_path):
        handler = "from nexy import redirect\n\n\ndef GET():\n    redirect('/target')\n"
        project = _web(tmp_path, {"src/routes/api/go.py": handler})
        status, headers, _ = request(project, ("/api/go", NO_HEADERS))[0]
        assert (status, headers["location"]) == (307, "/target")

    def test_a_handler_can_answer_not_found_as_json(self, tmp_path):
        handler = "from nexy import notFound\n\n\ndef GET():\n    notFound('Nobody')\n"
        project = _web(tmp_path, {"src/routes/api/who.py": handler})
        status, _, body = request(project, ("/api/who", JSON))[0]
        assert (status, "Nobody" in body) == (404, True)


class TestInADependency:
    GUARD = (
        "from nexy import unauthorized\n\n\n"
        "def require_login():\n    unauthorized(scheme='Bearer')\n\n\n"
        "dependencies = [require_login]\n"
    )

    def test_a_guard_closes_the_whole_folder_with_a_401(self, tmp_path):
        project = _web(
            tmp_path,
            {
                "src/routes/private/dependencies.py": self.GUARD,
                "src/routes/private/index.nexy": "<p>secret</p>\n",
            },
        )
        status, headers, body = request(project, ("/private", NO_HEADERS))[0]
        assert (status, "secret" in body) == (401, False)
        assert headers["www-authenticate"] == "Bearer"


class TestInAModularController:
    def test_a_controller_can_redirect(self, tmp_path):
        scaffold(tmp_path, "api-modular", "none")
        controller = (
            "from nexy import redirect\nfrom nexy.decorators import Controller\n\n\n"
            "@Controller()\nclass AppController:\n    async def get(self):\n"
            "        redirect('/elsewhere')\n"
        )
        write(tmp_path, "src/apps/app_controller.py", controller)
        status, headers, _ = request(tmp_path, ("/", NO_HEADERS))[0]
        assert (status, headers["location"]) == (307, "/elsewhere")
