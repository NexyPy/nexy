"""`useISRCache`: the store a project picks for its ISR pages."""

from __future__ import annotations

from nexy.core.config import Config


def test_the_default_store_is_the_process_memory(nexy_project):
    nexy_project()
    assert Config().useISRCache is None


def test_the_store_is_read_from_the_project_config(nexy_project):
    nexy_project('useISRCache = {"type": "file", "directory": ".cache/isr"}')
    assert Config().useISRCache == {"type": "file", "directory": ".cache/isr"}
