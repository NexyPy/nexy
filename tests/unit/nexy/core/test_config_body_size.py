"""`useMaxBodySize`: the largest request body a worker reads, in bytes; 0 turns the limit off."""

from __future__ import annotations

from nexy.core.config import Config


def test_use_max_body_size_defaults_to_one_mebibyte(nexy_project):
    nexy_project()
    assert Config().useMaxBodySize == 1024 * 1024


def test_use_max_body_size_is_read_from_the_project_config(nexy_project):
    nexy_project("useMaxBodySize = 10 * 1024 * 1024")
    assert Config().useMaxBodySize == 10 * 1024 * 1024


def test_use_max_body_size_zero_turns_the_limit_off(nexy_project):
    nexy_project("useMaxBodySize = 0")
    assert Config().useMaxBodySize == 0
