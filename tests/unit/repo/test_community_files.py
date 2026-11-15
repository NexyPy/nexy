"""The files a contributor reads on GitHub hold together: the addresses they give reach someone.

A report of conduct or of a vulnerability is sent to the address these files print, so a typo in
it loses the report without anyone knowing.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
MAILTO = re.compile(r"mailto:([^)\s\"']+)")


def _addresses(name: str) -> set[str]:
    return set(MAILTO.findall((ROOT / name).read_text(encoding="utf-8")))


def test_the_code_of_conduct_reports_to_the_address_the_issue_forms_give():
    assert _addresses("CODE_OF_CONDUCT.md") == _addresses(".github/ISSUE_TEMPLATE/config.yml")


def _form(name: str) -> dict:
    return yaml.safe_load((ROOT / ".github" / "ISSUE_TEMPLATE" / name).read_text(encoding="utf-8"))


def _field(form: dict, field_id: str) -> dict:
    return next((field for field in form["body"] if field.get("id") == field_id), {})


def test_a_bug_report_requires_a_link_to_a_minimal_reproduction():
    field = _field(_form("01_bug_report.yml"), "reproduction_link")
    assert field.get("validations", {}).get("required") is True


def test_a_bug_report_says_how_often_the_bug_happens():
    assert _field(_form("01_bug_report.yml"), "frequency").get("type") == "dropdown"


def test_a_bug_report_title_starts_with_its_kind():
    assert _form("01_bug_report.yml").get("title") == "Bug: "
