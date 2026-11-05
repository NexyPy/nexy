"""Regression tests for scripts/check_attribution.py.

The gate protects the contributor graph: an AI trailer makes GitHub list a bot
account next to the humans who own the work.
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "check_attribution.py"


def _load() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("check_attribution", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="checker")
def checker_fixture() -> types.ModuleType:
    return _load()


def test_offending_lines_rejects_ai_coauthor(checker: types.ModuleType) -> None:
    message = "feat: add router\n\nCo-Authored-By: Codebuff <noreply@codebuff.com>"

    assert checker.offending_lines(message) == ["Co-Authored-By: Codebuff <noreply@codebuff.com>"]


def test_offending_lines_rejects_generated_with_line(checker: types.ModuleType) -> None:
    message = "fix: guard dev server\n\nGenerated with [Claude Code](https://claude.com)"

    assert checker.offending_lines(message) == ["Generated with [Claude Code](https://claude.com)"]


def test_offending_lines_accepts_human_coauthor(checker: types.ModuleType) -> None:
    message = "feat: add router\n\nCo-Authored-By: Jane Doe <jane@example.com>"

    assert checker.offending_lines(message) == []


def test_offending_lines_accepts_plain_message(checker: types.ModuleType) -> None:
    message = "docs: explain the attribution policy\n\nHumans own their contributions."

    assert checker.offending_lines(message) == []


def test_main_rejects_message_file(
    checker: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text("feat: x\n\nCo-authored-by: Copilot <copilot@github.com>\n")
    monkeypatch.setattr(sys, "argv", ["check_attribution", "--message-file", str(message_file)])

    assert checker.main() == 1


def test_main_accepts_message_file(
    checker: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text("feat: add router\n")
    monkeypatch.setattr(sys, "argv", ["check_attribution", "--message-file", str(message_file)])

    assert checker.main() == 0


def test_human_sharing_a_tool_name_is_accepted(checker: types.ModuleType) -> None:
    for trailer in (
        "Co-authored-by: Ali Haider <ali@example.com>",
        "Co-authored-by: Devin Lee <devin.lee@corp.example>",
        "Co-authored-by: Sweep Patel <sweep@example.org>",
    ):
        assert checker.offending_lines(f"fix\n\n{trailer}\n") == []


def test_ai_identities_are_still_rejected(checker: types.ModuleType) -> None:
    for trailer in (
        "Co-Authored-By: Claude Sonnet <noreply@anthropic.com>",
        "Co-authored-by: Copilot <noreply@github.com>",
        "Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
        "Co-authored-by: Some Agent <agent@openai.com>",
    ):
        assert checker.offending_lines(f"fix\n\n{trailer}\n") == [trailer], trailer


def test_assisted_by_names_the_tool(checker: types.ModuleType) -> None:
    assert checker.offending_lines("fix\n\nAssisted-by: Cursor\n") == ["Assisted-by: Cursor"]


@pytest.mark.parametrize(
    "identity",
    [
        "copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>",
        "Copilot <223556219+Copilot@users.noreply.github.com>",
        "GitHub Copilot <copilot@github.com>",
        "devin-ai-integration[bot] <158243242+devin-ai-integration[bot]@users.noreply.github.com>",
        "google-labs-jules[bot] <161369871+google-labs-jules[bot]@users.noreply.github.com>",
        "cursoragent <cursoragent@cursor.com>",
        "Cursor Agent <agent@cursor.sh>",
        "Claude <noreply@anthropic.com>",
        "John Doe (aider) <john@example.com>",
        "chatgpt-codex-connector[bot] <1+chatgpt-codex-connector[bot]@users.noreply.github.com>",
    ],
)
def test_is_ai_author_rejects_an_agent(checker: types.ModuleType, identity: str) -> None:
    assert checker.is_ai_author(identity)


@pytest.mark.parametrize(
    "identity",
    [
        "Espoir LOEMBA <108950035+Espoir-Loem@users.noreply.github.com>",
        "GitHub <noreply@github.com>",
        "Devin Lee <devin@corp.com>",
        "Ali Haider <ali@example.com>",
        "dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
    ],
)
def test_is_ai_author_accepts_a_person_or_a_tool_bot(
    checker: types.ModuleType, identity: str
) -> None:
    assert not checker.is_ai_author(identity)


def test_offending_identities_names_the_role_of_an_agent(checker: types.ModuleType) -> None:
    found = checker.offending_identities(
        "cursoragent <cursoragent@cursor.com>", "GitHub <noreply@github.com>"
    )

    assert found == ["Author: cursoragent <cursoragent@cursor.com>"]


def test_offending_identities_is_empty_for_a_person(checker: types.ModuleType) -> None:
    person = "Espoir LOEMBA <108950035+Espoir-Loem@users.noreply.github.com>"

    assert checker.offending_identities(person, person) == []


def test_main_rejects_a_commit_made_by_an_agent_identity(
    checker: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text("feat: add router\n")
    agent = "cursoragent <cursoragent@cursor.com>"
    monkeypatch.setattr(checker, "current_identities", lambda: (agent, agent))
    monkeypatch.setattr(sys, "argv", ["check_attribution", "--message-file", str(message_file)])

    assert checker.main() == 1


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> None:
    import os
    import subprocess

    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, env={**os.environ, **(env or {})}
    )


def test_main_rejects_a_range_authored_by_an_agent(
    checker: types.ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    agent = {
        "GIT_AUTHOR_NAME": "google-labs-jules[bot]",
        "GIT_AUTHOR_EMAIL": "161369871+google-labs-jules[bot]@users.noreply.github.com",
        "GIT_COMMITTER_NAME": "Human",
        "GIT_COMMITTER_EMAIL": "human@example.com",
    }
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "commit", "-q", "--allow-empty", "-m", "feat: x", env=agent)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check_attribution", "--range", "HEAD"])

    assert checker.main() == 1


@pytest.mark.parametrize(
    "line",
    [
        "Co-Authored-By: opencode <noreply@opencode.ai>",
        "Generated with [opencode](https://opencode.ai)",
        "Co-authored-by: Freebuff <noreply@freebuff.com>",
        "Generated with Freebuff",
        "Co-authored-by: Qoder <noreply@qoder.com>",
        "Generated with Qoder CLI",
    ],
)
def test_offending_lines_rejects_opencode_freebuff_and_qoder(
    checker: types.ModuleType, line: str
) -> None:
    assert checker.offending_lines(f"feat: x\n\n{line}") == [line]


@pytest.mark.parametrize(
    "identity",
    ["opencode <noreply@opencode.ai>", "Freebuff <bot@freebuff.com>", "qodercli <cli@qoder.com>"],
)
def test_is_ai_author_rejects_opencode_freebuff_and_qoder(
    checker: types.ModuleType, identity: str
) -> None:
    assert checker.is_ai_author(identity)
