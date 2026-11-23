import shutil
import subprocess

import pytest

from nexy.modules.frontend.islands import ISLANDS_RUNTIME


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


# A stub window whose IntersectionObserver writes the id of the element it watches.
_WATCHED = """
globalThis.window = { IntersectionObserver: class {
  observe(target) { console.log(target.id) }
} };
globalThis.IntersectionObserver = window.IntersectionObserver;
"""


def _watched(container: str) -> str:
    script = (
        _WATCHED
        + ISLANDS_RUNTIME
        + f"\nconst parent = {{ id: 'parent' }};\nconst el = {container};\n"
        + "nexyIslands.schedule(el, 'client:visible', () => {});\n"
    )
    done = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return done.stdout.strip()


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_visible_watches_first_child_of_contents_container():
    # The container is `display: contents`: it has no box, so it never intersects.
    container = "{ id: 'ncc', firstElementChild: { id: 'child' }, parentElement: parent }"
    assert _watched(container) == "child"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_visible_watches_parent_of_empty_container():
    container = "{ id: 'ncc', firstElementChild: null, parentElement: parent }"
    assert _watched(container) == "parent"
