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
