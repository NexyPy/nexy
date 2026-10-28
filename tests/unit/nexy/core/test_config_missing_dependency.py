"""A package that nexyconfig.py needs but this Python lacks must be named, not hidden.

`nexyconfig.py` of a modular project imports its modules, which import their ORM. When that
package is missing (the project's virtual environment is not the active one), the config used to
count as "no nexyconfig.py": the defaults applied without the aliases, and the first error the
developer saw was about an alias, not about the missing package.
"""

from __future__ import annotations

import sys

import pytest

from nexy.core.config import Config

MISSING = "package_that_is_not_installed_anywhere"


@pytest.fixture
def broken_config(nexy_project):
    nexy_project(imports=f"import {MISSING}")
    Config()
    return Config.get_load_error()


def test_the_missing_package_is_named(broken_config):
    assert MISSING in (broken_config or "")


def test_the_message_says_how_to_recover(broken_config):
    assert "virtual environment" in (broken_config or "")


@pytest.mark.usefixtures("broken_config")
def test_the_config_is_refused_instead_of_replaced_by_defaults():
    with pytest.raises(ValueError, match=MISSING):
        Config.require_valid()


@pytest.mark.usefixtures("nexy_project")
def test_a_project_without_nexyconfig_still_runs_on_the_defaults():
    # The fixture put the test in an empty folder and restores Config afterwards.
    sys.modules.pop("nexyconfig", None)
    Config.reset()
    Config()
    Config.require_valid()
