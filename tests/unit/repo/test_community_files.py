"""The files a contributor reads on GitHub hold together: the addresses they give reach someone.

A report of conduct or of a vulnerability is sent to the address these files print, so a typo in
it loses the report without anyone knowing.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAILTO = re.compile(r"mailto:([^)\s\"']+)")


def _addresses(name: str) -> set[str]:
    return set(MAILTO.findall((ROOT / name).read_text(encoding="utf-8")))


def test_the_code_of_conduct_reports_to_the_address_the_issue_forms_give():
    assert _addresses("CODE_OF_CONDUCT.md") == _addresses(".github/ISSUE_TEMPLATE/config.yml")
