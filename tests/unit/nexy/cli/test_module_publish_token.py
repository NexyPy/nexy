"""The publish token comes from the environment or from a future login file."""

from __future__ import annotations

from pathlib import Path

from nexy.modules.cli.publish.token import LOGIN_FILE, TOKEN_ENV, resolve_token


def login(home: Path, value: str) -> None:
    path = home / LOGIN_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def test_resolve_token_reads_the_environment(tmp_path):
    assert resolve_token({TOKEN_ENV: "from-env"}, tmp_path) == "from-env"


def test_resolve_token_reads_the_login_file(tmp_path):
    login(tmp_path, "from-file\n")
    assert resolve_token({}, tmp_path) == "from-file"


def test_resolve_token_prefers_the_environment(tmp_path):
    login(tmp_path, "from-file")
    assert resolve_token({TOKEN_ENV: "from-env"}, tmp_path) == "from-env"


def test_resolve_token_ignores_an_empty_environment_value(tmp_path):
    login(tmp_path, "from-file")
    assert resolve_token({TOKEN_ENV: ""}, tmp_path) == "from-file"


def test_resolve_token_strips_surrounding_whitespace(tmp_path):
    assert resolve_token({TOKEN_ENV: "  from-env\n"}, tmp_path) == "from-env"


def test_resolve_token_returns_an_empty_string_when_no_source_exists(tmp_path):
    assert resolve_token({}, tmp_path) == ""


def test_resolve_token_ignores_an_empty_login_file(tmp_path):
    login(tmp_path, "  \n")
    assert resolve_token({}, tmp_path) == ""


def test_resolve_token_ignores_an_unreadable_login_file(tmp_path):
    (tmp_path / LOGIN_FILE).mkdir(parents=True)
    assert resolve_token({}, tmp_path) == ""
