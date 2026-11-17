"""`useDocs`: where the API reference and its schema are served; "dev" keeps them off production."""

from __future__ import annotations

from nexy.core.config import Config


def test_use_docs_defaults_to_the_dev_server_only(nexy_project):
    nexy_project()
    assert Config().useDocs == "dev"


def test_use_docs_true_is_read_from_the_project_config(nexy_project):
    nexy_project("useDocs = True")
    assert Config().useDocs is True
