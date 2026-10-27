"""The code of docs/guides/recipes.md runs: every block with a `filename` becomes a project file."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest

from tests.e2e.project import REPO, scaffold, write

RECIPES = REPO / "docs" / "guides" / "recipes.md"
BLOCK = re.compile(r'```\w+ filename="([^"]+)"\n(.*?)```', re.DOTALL)

SCENARIO = """
import json, sys
sys.path.insert(0, ".")
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build(showlog=False)
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer

client = TestClient(AppServer().run(), raise_server_exceptions=False)
login = {"name": "ada", "password": "lovelace"}
seen = {}
seen["anonymous"] = client.get("/api/account").status_code
seen["wrong"] = client.post("/api/login", json={**login, "password": "x"}).status_code
seen["login"] = client.post("/api/login", json=login).status_code
seen["account"] = client.get("/api/account").json()
client.post("/api/logout")
seen["after_logout"] = client.get("/api/account").status_code
seen["empty"] = client.get("/api/notes").json()
seen["created"] = client.post("/api/notes", json={"title": "milk"}).json()
seen["invalid"] = client.post("/api/notes", json={}).status_code
seen["read"] = client.get("/api/notes/1").json()
seen["missing"] = client.get("/api/notes/9").status_code
seen["deleted"] = client.delete("/api/notes/1").json()
seen["left"] = client.get("/api/notes").json()
sent = {"file": ("../../etc/passwd", b"hello")}
seen["upload"] = client.post("/api/upload", files=sent).json()
seen["too_big"] = client.post("/api/upload", files={"file": ("a", b"x" * 1_000_001)}).status_code
sys.stdout.write("@@" + json.dumps(seen) + "@@")
"""


@pytest.fixture(scope="module")
def seen(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    project = tmp_path_factory.mktemp("recipes")
    scaffold(project)
    files = BLOCK.findall(RECIPES.read_text(encoding="utf-8"))
    assert files, "recipes.md has no file blocks"
    for name, code in files:
        write(project, name, code)
    done = subprocess.run(
        [sys.executable, "-c", SCENARIO],
        cwd=project,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    assert "@@" in done.stdout, done.stderr[-1500:]
    result: dict[str, object] = json.loads(done.stdout.split("@@")[1])
    return result


def test_a_visitor_is_refused_before_signing_in(seen):
    assert seen["anonymous"] == 401


def test_a_wrong_password_is_refused(seen):
    assert seen["wrong"] == 401


def test_signing_in_opens_the_account(seen):
    assert (seen["login"], seen["account"]) == (200, {"user": "ada"})


def test_signing_out_closes_the_account_again(seen):
    assert seen["after_logout"] == 401


def test_the_notes_start_empty(seen):
    assert seen["empty"] == []


def test_a_note_is_created_and_read_back(seen):
    assert seen["created"] == seen["read"] == {"id": 1, "title": "milk"}


def test_a_note_without_a_title_is_invalid(seen):
    assert seen["invalid"] == 422


def test_an_unknown_note_is_not_found(seen):
    assert seen["missing"] == 404


def test_a_deleted_note_is_gone(seen):
    assert (seen["deleted"], seen["left"]) == ({"deleted": True}, [])


def test_an_upload_keeps_only_the_file_name(seen):
    assert seen["upload"] == {"name": "passwd", "size": 5}


def test_an_oversized_upload_is_refused(seen):
    assert seen["too_big"] == 413
