"""The deployment registry holds files, not platform code imported by the framework."""

import ast
import json
from pathlib import Path

from nexy.modules.cli.deployment import GITIGNORE_LINES, PLATFORM_FILES

VERCEL = PLATFORM_FILES["vercel"]


def test_registry_describes_the_vercel_files():
    assert set(VERCEL) == {Path("src", "server.py"), Path("vercel.json")}


def test_entry_point_source_is_valid_python():
    assert isinstance(ast.parse(VERCEL[Path("src", "server.py")]), ast.Module)


def test_host_config_has_two_cache_rules():
    assert len(json.loads(VERCEL[Path("vercel.json")])["headers"]) == 2


def test_ignore_lines_are_unique():
    assert len(set(GITIGNORE_LINES)) == len(GITIGNORE_LINES)
