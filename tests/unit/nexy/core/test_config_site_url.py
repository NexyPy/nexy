"""`useSiteUrl`: the public origin of the site, which the sitemap writes its URLs with (#84)."""

from __future__ import annotations

from nexy.core.config import Config


def test_use_site_url_is_unset_by_default(nexy_project):
    nexy_project()
    assert Config().useSiteUrl is None


def test_use_site_url_is_read_from_the_project_config(nexy_project):
    nexy_project('useSiteUrl = "https://example.com"')
    assert Config().useSiteUrl == "https://example.com"
