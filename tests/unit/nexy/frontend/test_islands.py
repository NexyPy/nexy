from nexy.frontend.islands import ISLANDS_RUNTIME


class TestIslandsRuntime:
    """The islands runtime must honor client: directives to defer hydration."""

    def test_contains_request_idle_callback(self):
        assert "requestIdleCallback" in ISLANDS_RUNTIME

    def test_contains_intersection_observer(self):
        assert "IntersectionObserver" in ISLANDS_RUNTIME

    def test_contains_match_media(self):
        assert "matchMedia" in ISLANDS_RUNTIME

    def test_contains_client_only_placeholder(self):
        assert "client:only" in ISLANDS_RUNTIME
        assert "nexy-island" in ISLANDS_RUNTIME

    def test_default_directive_is_load(self):
        assert "client:load" in ISLANDS_RUNTIME

    def test_idle_fallback_uses_set_timeout(self):
        assert "setTimeout" in ISLANDS_RUNTIME

    def test_visible_uses_observer_with_root_margin(self):
        assert "rootMargin" in ISLANDS_RUNTIME
