"""The browser side of an action: the call, its errors, the page refresh and the state."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


@pytest.fixture(scope="module")
def seen() -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "actions_scenarios.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


class TestCall:
    def test_the_input_is_posted_as_json(self, seen):
        assert seen["request"] == {
            "url": "/_nx_abc",
            "method": "POST",
            "body": '{"name":"Ada"}',
            "type": "application/json",
        }

    def test_the_answer_is_returned_parsed(self, seen):
        assert seen["result"] == {"name": "Ada"}

    def test_the_action_knows_its_url_for_a_form_without_javascript(self, seen):
        assert seen["metadata"] == {"url": "/_nx_abc", "id": "src.actions.create"}


class TestErrors:
    def test_an_invalid_input_names_its_fields(self, seen):
        assert seen["invalid"]["error"]["fields"] == {"name": "Field required"}

    def test_the_error_carries_the_status(self, seen):
        assert (seen["invalid"]["error"]["name"], seen["invalid"]["error"]["status"]) == (
            "ActionError",
            422,
        )

    def test_a_text_detail_is_the_message(self, seen):
        assert seen["forbidden"]["error"]["message"] == "no"

    def test_an_answer_that_is_not_json_still_fails_cleanly(self, seen):
        assert seen["crash"]["error"]["status"] == 500


class TestRevalidate:
    def test_the_current_page_reloads_without_a_router(self, seen):
        assert seen["reloadOnStar"] == 1

    def test_another_page_is_left_alone(self, seen):
        assert seen["reloadOtherPage"] == 1

    def test_a_listed_current_page_reloads(self, seen):
        assert seen["reloadListedPage"] == 2

    def test_the_router_refreshes_instead_of_reloading(self, seen):
        assert seen["routerRefresh"] == {"refreshed": 1, "reloaded": 2}

    def test_an_answer_without_the_header_does_nothing(self, seen):
        assert seen["noHeaderNoReload"] == 0


class TestState:
    def test_a_run_goes_from_pending_to_data(self, seen):
        assert seen["state"]["states"] == [
            {"pending": True, "data": None, "error": False},
            {"pending": False, "data": {"id": 1}, "error": False},
        ]

    def test_a_run_resolves_with_the_data(self, seen):
        assert seen["state"]["data"] == {"id": 1}

    def test_a_failed_run_resolves_with_nothing_and_keeps_the_error(self, seen):
        assert seen["failedRun"] is None
        assert seen["failedState"] == {"pending": False, "error": "ActionError"}

    def test_the_error_callback_runs(self, seen):
        assert seen["onError"] is True

    def test_reset_forgets_the_error(self, seen):
        assert seen["afterReset"] == {"pending": False, "error": None}
