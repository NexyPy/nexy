"""The tutorial runs: its chapters, replayed in order, build the app each one promises.

Every block with a `filename` is a whole file. A chapter writes the blocks every reader sees, then
the blocks of the router variant the run follows, and the requests of the chapter must answer
what the page says they answer.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from tests.e2e.project import REPO, scaffold, write

TUTORIAL = REPO / "docs" / "tutorial"
BLOCK = re.compile(r'```\w+ filename="([^"]+)"\n(.*?)```', re.DOTALL)
SHELL = re.compile(r"```bash\n(.*?)```", re.DOTALL)
# The reader's virtual environment is activated: its tools, such as `alembic`, are on the PATH.
ACTIVATED = f"{Path(sys.executable).parent}{os.pathsep}{os.environ.get('PATH', '')}"
NX = "import sys; from nexy.modules.cli import CLI; sys.argv[0] = 'nx'; CLI()"
VARIANT = re.compile(r"<!-- router:([a-z, ]+) -->(.*?)<!-- /router -->", re.DOTALL)
TEMPLATES = {"fbr": "web-fbr", "modular": "web-modular"}

# The chapters in reading order, and what each one makes the app answer.
CHAPTERS: list[tuple[str, list[tuple[str, int, str]]]] = [
    ("create-the-project", [("/", 200, "")]),
    ("pages-and-layouts", [("/notes", 200, "<li>Buy milk</li>")]),
    (
        "dynamic-routes",
        [
            ("/notes/1", 200, "<h1>Buy milk</h1>"),
            ("/notes/9", 404, ""),
            ("/api/notes", 200, '{"id":2,"text":"Ship Nexy"}'),
        ],
    ),
    ("components", [("/notes", 200, '<article class="note">')]),
    (
        "store-the-notes",
        [
            ("/notes", 200, "Ship Nexy</a>"),
            ("/notes/1", 200, "<h1>Buy milk</h1>"),
            ("/api/notes", 200, '"text":"Buy milk"'),
        ],
    ),
    (
        "create-a-note",
        [
            ("FORM /notes text=Read the docs", 303, "/notes"),
            ("/notes", 200, "Read the docs</a>"),
            ('FORM /notes text=<b>Say "hi"</b>', 303, "/notes"),
            ("/notes", 200, "&lt;b&gt;Say &#34;hi&#34;&lt;/b&gt;</a>"),
            ("/notes/4", 200, "<h1>&lt;b&gt;Say"),
        ],
    ),
    (
        "validation-errors",
        [
            ("FORM /notes text=   ", 303, "/notes?error=A+note+cannot+be+blank."),
            ("/notes?error=A+note+cannot+be+blank.", 200, "A note cannot be blank.</p>"),
            ("FORM /notes text=Write tests", 303, ""),
            ("/notes", 200, "Write tests</a>"),
        ],
    ),
    (
        "edit-and-delete",
        [
            ("FORM /notes/1#1 note_id=1&text=Buy oat milk", 303, "/notes/1"),
            ("/notes/1", 200, "<h1>Buy oat milk</h1>"),
            ("FORM /notes/1#1 note_id=1&text= ", 303, "/notes/1?error=A+note+cannot+be+blank."),
            ("FORM /notes/1#2 note_id=1", 303, "/notes"),
            ("/notes/1", 404, ""),
        ],
    ),
    (
        "paginate-the-notes",
        [
            ("FORM /notes text=Note 1", 303, "/notes"),
            ("FORM /notes text=Note 2", 303, "/notes"),
            ("FORM /notes text=Note 3", 303, "/notes"),
            ("FORM /notes text=Note 4", 303, "/notes"),
            ("FORM /notes text=Note 5", 303, "/notes"),
            ("/notes", 200, 'href="/notes?page=2" rel="next"'),
            ("/notes?page=2", 200, 'rel="prev">Newer</a>'),
            ("/notes?page=abc", 200, "<h1>Notes</h1>"),
        ],
    ),
    (
        "accounts",
        [
            ("/notes/2", 200, "<h1>Ship Nexy</h1>"),
            ("FORM /signup email=ada@example.com&password=short", 303, "/signup?error="),
            ("FORM /signup email=ada@example.com&password=lovelace99", 303, "/notes"),
            ("/notes", 200, "Sign out</button>"),
            ("FORM /notes email=x", 303, "/"),
            ("/notes", 200, '<a href="/signup">create an account</a>'),
            ("FORM /signup email=ada@example.com&password=lovelace99", 303, "already+has"),
            ("FORM /signin email=ada@example.com&password=wrong-pass", 303, "/signin?error=Wrong"),
            ("FORM /signin email=ADA@example.com&password=lovelace99", 303, "/notes"),
            ("/notes", 200, "Sign out</button>"),
        ],
    ),
    (
        "own-notes",
        [
            ("/notes", 200, "<h1>Sign in</h1>"),
            ("FORM /signin email=ada@example.com&password=lovelace99", 303, "/notes"),
            ("/notes", 200, "No notes yet"),
            ("/notes/2", 404, ""),
            ("FORM /notes#2 text=Ada's first", 303, "/notes"),
            ("/notes", 200, "Ada&#39;s first</a>"),
            ("/api/notes", 200, '"user_id":1'),
            ("FORM /notes#1 x=1", 303, "/"),
            ("/notes/3", 200, "<h1>Sign in</h1>"),
            ("/api/notes", 401, ""),
        ],
    ),
    (
        "password-reset",
        [
            ("FORM /forgot email=nobody@example.com", 303, "/forgot?sent=1"),
            ("/forgot?sent=1", 200, "a link to reset its password is on its way"),
            ("FORM /forgot email=ada@example.com", 303, "Subject: Reset your password"),
            ("{link}", 200, "<h1>Choose a new password</h1>"),
            ("FORM {link} password=short", 303, "error=A+password"),
            ("FORM {link} password=babbage123", 303, "/signin?reset=1"),
            ("/signin?reset=1", 200, "Your password is changed"),
            ("FORM {link} password=again12345", 303, "/forgot?error="),
            ("FORM /signin email=ada@example.com&password=lovelace99", 303, "error=Wrong"),
            ("FORM /signin email=ada@example.com&password=babbage123", 303, "/notes"),
        ],
    ),
    (
        "search-the-notes",
        [
            ("FORM /signin email=ada@example.com&password=babbage123", 303, "/notes"),
            ("/notes", 200, 'data-nexy-path="/src/components/NoteSearch.tsx"'),
            ("/notes", 200, "&quot;text&quot;: &quot;Ada&#x27;s first&quot;"),
        ],
    ),
    (
        "tick-a-note",
        [
            ("FORM /signin email=ada@example.com&password=babbage123", 303, "/notes"),
            ("/notes", 200, 'aria-pressed="false">To do</button>'),
            ("FORM /notes#3", 303, "/notes"),
            ("/notes", 200, 'aria-pressed="true">Done</button>'),
            ("FETCH /notes#3", 200, "false"),
            ("/notes", 200, 'aria-pressed="false">To do</button>'),
            ("FETCH /notes#3 note_id=2", 404, ""),
        ],
    ),
]

RUNNER = """
import contextlib, html, io, json, re, sys
sys.path.insert(0, ".")
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
Builder().build(showlog=False)
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer

client = TestClient(AppServer().run(), raise_server_exceptions=False)
FORM = re.compile(r'<form method="post" action="([^"]+)"(.*?)</form>', re.S)
HIDDEN = re.compile(r'<input type="hidden" name="([^"]+)" value="([^"]*)"')


def form_of(page):
    page, _, nth = page.partition("#")
    form = client.get(page, headers={"accept": "text/html"}).text
    action, inside = FORM.findall(form)[int(nth or 1) - 1]
    return page, action, {name: html.unescape(value) for name, value in HIDDEN.findall(inside)}


def submit(page, fields):
    page, action, hidden = form_of(page)
    headers = {"accept": "text/html", "referer": "http://testserver" + page}
    return client.post(action, data=hidden | fields, headers=headers, follow_redirects=False)


def fetch(page, fields):
    _, action, hidden = form_of(page)
    sent = hidden | fields
    data = {key: int(value) if value.isdigit() else value for key, value in sent.items()}
    headers = {"accept": "application/json"}
    return client.post(action, json=data, headers=headers, follow_redirects=False)


def ask(path):
    kind, _, rest = path.partition(" ")
    if kind in ("FORM", "FETCH"):
        page, _, query = rest.partition(" ")
        fields = dict(pair.split("=", 1) for pair in query.split("&") if pair)
        return (submit if kind == "FORM" else fetch)(page, fields)
    accept = "application/json" if path.startswith("/api/") else "text/html"
    return client.get(path, headers={"accept": accept})


seen, link = [], ""
for path in json.loads(sys.argv[1]):
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        answer = ask(path.replace("{link}", link))
    link = next(iter(re.findall(r"http://localhost:3000(/\\S+)", printed.getvalue())), link)
    seen.append([answer.status_code, answer.headers.get("location", "") + printed.getvalue()
                 + answer.text])
sys.stdout.write("@@" + json.dumps(seen) + "@@")
"""


def chapter(page: Path, router: str) -> str:
    """The chapter one router's reader sees: the other routers' variants taken out, in place."""

    def keep(found: re.Match[str]) -> str:
        return found[2] if router in found[1].replace(" ", "").split(",") else ""

    return VARIANT.sub(keep, page.read_text(encoding="utf-8"))


def commands(text: str) -> list[list[str]]:
    """The `nx` and `python` lines of the shell blocks; installs and the dev server are not run."""
    lines = [line.strip() for block in SHELL.findall(text) for line in block.splitlines()]
    return [shlex.split(line) for line in lines if line.startswith(("nx ", "python "))]


def run(project: Path, argv: list[str]) -> None:
    program = [sys.executable, "-c", NX] if argv[0] == "nx" else [sys.executable]
    done = subprocess.run(
        [*program, *argv[1:]],
        cwd=project,
        env={**os.environ, "PYTHONPATH": f"{project}{os.pathsep}{REPO}", "PATH": ACTIVATED},
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert done.returncode == 0, f"{' '.join(argv)}: {done.stdout[-800:]}{done.stderr[-800:]}"


def replay(project: Path, paths: list[str]) -> list[tuple[int, str]]:
    done = subprocess.run(
        [sys.executable, "-c", RUNNER, json.dumps(paths)],
        cwd=project,
        env={**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    assert "@@" in done.stdout, done.stderr[-1500:]
    return [tuple(pair) for pair in json.loads(done.stdout.split("@@")[1])]


@pytest.fixture(scope="module", params=sorted(TEMPLATES))
def answers(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory):
    """Every chapter, written in order into one project, and the answers after each chapter."""
    router = request.param
    project = tmp_path_factory.mktemp(f"tutorial-{router}")
    scaffold(project, TEMPLATES[router], framework="react")
    seen: dict[str, list[tuple[int, str]]] = {}
    for slug, checks in CHAPTERS:
        text = chapter(TUTORIAL / f"{slug}.md", router)
        for name, code in BLOCK.findall(text):
            write(project, name, code)
        for argv in commands(text):
            run(project, argv)
        seen[slug] = replay(project, [path for path, _, _ in checks])
    return seen


@pytest.mark.parametrize(
    ("slug", "index"),
    [(slug, index) for slug, checks in CHAPTERS for index in range(len(checks))],
)
def test_a_chapter_answers_what_it_promises(answers, slug, index):
    path, status, needle = dict(CHAPTERS)[slug][index]
    code, body = answers[slug][index]
    assert (code, needle in body) == (status, True), f"{path}: {body[:300]}"
