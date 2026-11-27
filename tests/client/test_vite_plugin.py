"""The Nexy Vite plugin builds the static pages after `vite build`, never when `vite` dev stops."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
BUILDING = "[nexy] Building client bundles..."


def _run(command: str) -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "vite_plugin.mjs"), command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_closing_the_dev_server_builds_nothing():
    assert _run("serve") == {"logged": [], "ran": [], "error": None}


def test_closing_a_build_builds_the_client_bundles():
    assert BUILDING in _run("build")["logged"]


def test_closing_a_failed_build_builds_nothing():
    assert BUILDING not in _run("build-failed")["logged"]


def test_the_dev_server_never_warms_up_a_declaration_file():
    # A `.d.ts` only types code; esbuild reads `export const X: T;` as an error (#620).
    assert "!src/**/*.d.ts" in _run("warmup")["warmup"]


def test_the_dev_base_follows_the_setting():
    assert _run("base") == {"base": "/app/", "error": None}


def test_the_dev_plugin_supplies_a_synchronous_react_preamble():
    assert "injectIntoGlobalHook(window)" in _run("preamble")["preamble"]["code"]


def test_the_build_plugin_omits_the_dev_only_react_preamble():
    assert _run("preamble-prod")["preamble"]["code"] == ""


def test_the_build_base_follows_the_setting():
    assert _run("base-prod") == {"base": "/app/__nexy__/client/", "error": None}


def test_the_dev_server_still_warms_up_the_typescript_modules():
    assert any(pattern.endswith(",ts,js}") for pattern in _run("warmup")["warmup"])


def test_a_batch_of_files_puts_each_path_on_its_own_line():
    first = _run("log")["infos"][0]
    assert first == (
        "vite » hmr update /src/components/templates/services-section.tsx\n"
        "vite » hmr update /src/components/templates/products-section.tsx\n"
        "vite » hmr update /src/globale.css"
    )


def test_a_page_reload_keeps_the_leading_slash():
    assert "vite » page reload /src/i18n/dictionaries.ts" in _run("log")["infos"]


def test_no_path_is_mangled_by_stripping_a_slash():
    assert "srci18n" not in " ".join(_run("log")["infos"])


def test_two_identical_updates_are_printed_once():
    assert _run("log")["infos"].count("vite » hmr update /src/unique.css") == 1
