"""The state behind useFetch: one request per URL, shared, kept while it refreshes."""

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
        [NODE, str(HERE / "fetch_scenarios.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


class TestLoad:
    def test_a_new_state_is_pending_without_data(self, seen):
        assert seen["before"] == {"data": None, "pending": True, "error": None}

    def test_the_answer_becomes_the_data(self, seen):
        assert seen["loaded"] == {"data": [{"id": 1}], "pending": False, "error": None}

    def test_the_request_asks_for_json_with_the_cookies(self, seen):
        assert seen["request"] == {
            "url": "/api/users",
            "accept": "application/json",
            "credentials": "same-origin",
        }

    def test_a_subscriber_hears_the_change(self, seen):
        assert seen["notified"] >= 1


class TestSharing:
    def test_a_second_state_on_the_same_url_reuses_the_answer(self, seen):
        assert seen["sharedWithoutRefetch"] == {"calls": 1, "data": [{"id": 1}]}

    def test_the_data_stays_while_it_refreshes(self, seen):
        assert seen["whileRefreshing"] == {"data": [{"id": 1}], "pending": True, "error": None}

    def test_two_refreshes_at_once_send_one_request(self, seen):
        assert seen["deduplicated"] == {"calls": 2, "data": [{"id": 1}, {"id": 2}]}

    def test_refresh_all_reloads_every_url_loaded(self, seen):
        assert seen["refreshAll"] == ["/api/broken", "/api/posts/9", "/api/users"]

    def test_a_revalidate_event_reloads_every_url_loaded(self, seen):
        assert seen["revalidateEvent"] == 3


class TestErrors:
    def test_an_error_status_is_a_fetch_error_with_its_detail(self, seen):
        assert seen["notFound"]["error"] == {
            "name": "FetchError",
            "status": 404,
            "message": "No such post",
        }

    def test_an_error_ends_the_pending_state(self, seen):
        assert seen["notFound"]["pending"] is False

    def test_an_answer_that_is_not_json_still_fails_cleanly(self, seen):
        assert seen["crash"]["error"]["status"] == 500
