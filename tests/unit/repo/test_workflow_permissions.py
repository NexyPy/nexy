"""Every workflow says what its token may do; nothing runs with the default permissions (#612)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.stem)
def test_a_workflow_declares_the_permissions_of_its_token(path):
    assert "permissions" in yaml.safe_load(path.read_text("utf-8"))
