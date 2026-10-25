"""The client build of a Vue or Svelte root layout loses ``<html>``, ``<head>`` and ``<body>``.

Neither framework can create those elements in the browser, so the browser builds the body content
only; the server renders the full document. The stripper must read tags the way a parser does:
quotes and braces can contain ``>``.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is not installed")


def _strip(kind: str, source: str) -> str:
    done = subprocess.run(
        [NODE, str(HERE / "strip.mjs"), json.dumps([{"kind": kind, "source": source}])],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    if "ERR_UNKNOWN_FILE_EXTENSION" in done.stderr:
        pytest.skip("this Node.js cannot run TypeScript")
    assert "@@" in done.stdout, done.stderr[-800:]
    return json.loads(done.stdout.split("@@")[1])[0]


SVELTE = (
    "<script>let { children } = $props();</script>\n"
    '<html lang="en" class={dark ? "d" : "l"}><head><title>T</title><script>x()</script></head>\n'
    '<body class="a>b"><main>{@render children()}</main></body></html>\n'
)


def test_svelte_keeps_only_the_body_content():
    out = _strip("svelte", SVELTE)
    assert "<html" not in out and "<head" not in out and "<body" not in out
    assert "</html>" not in out and "</body>" not in out and "<title>" not in out
    assert "<main>{@render children()}</main>" in out
    assert "let { children } = $props();" in out


def test_attribute_values_with_a_closing_angle_bracket_do_not_end_the_tag():
    assert '>b"' not in _strip("svelte", SVELTE)


def test_vue_only_touches_the_template_block():
    source = (
        '<template><html lang="en"><head><script>t()</script></head>'
        "<body><slot /></body></html></template>\n"
        '<script setup>const html = "<html>"</script>\n'
    )
    out = _strip("vue", source)
    assert "<template><slot /></template>" in out
    assert 'const html = "<html>"' in out


def test_a_layout_without_document_tags_is_unchanged():
    source = "<template><div><slot /></div></template>\n"
    assert _strip("vue", source) == source
