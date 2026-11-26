"""`useRateLimit`: the requests one client address may send per window; None turns it off."""

from __future__ import annotations

from nexy.core.config import Config


def test_use_rate_limit_is_off_by_default(nexy_project):
    nexy_project()
    assert Config().useRateLimit is None


def test_use_rate_limit_is_read_from_the_project_config(nexy_project):
    nexy_project('useRateLimit = {"requests": 60, "per": 60}')
    assert Config().useRateLimit == {"requests": 60, "per": 60}
