"""useFetch behaves the same in every framework: pending, then the data, shared and refreshed."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")

FRAMEWORKS = ("react",)


@pytest.fixture(scope="module", params=FRAMEWORKS)
def story(request: pytest.FixtureRequest) -> dict:
    done = subprocess.run(
        [NODE, "--conditions=browser", "fetch_adapters.mjs", request.param],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_use_fetch_is_pending_on_the_first_paint(story):
    assert story["firstPaint"] == {"a": "pending", "b": "pending", "c": "pending"}


def test_use_fetch_shows_the_data_once_loaded(story):
    assert (story["loaded"]["a"], story["loaded"]["b"]) == ('[{"id":1}]', '[{"id":1}]')


def test_use_fetch_sends_one_request_for_two_readers(story):
    assert story["loaded"]["calls"] == 1


def test_use_fetch_shows_the_status_of_an_error(story):
    assert story["loaded"]["c"] == "error:404"


def test_use_fetch_refresh_updates_every_reader(story):
    assert (story["refreshed"]["a"], story["refreshed"]["b"]) == (
        '[{"id":1},{"id":2}]',
        '[{"id":1},{"id":2}]',
    )


def test_use_fetch_refresh_sends_one_more_request(story):
    assert story["refreshed"]["calls"] == 2


def test_use_fetch_logs_no_error(story):
    assert story["errors"] == []
