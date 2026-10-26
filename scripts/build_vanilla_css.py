"""Compile the starter's Tailwind stylesheet into the plain CSS of the "vanilla" style.

A project that picks "Vanilla CSS" in `nx new` gets the same look without any CSS tool. That
stylesheet is the Tailwind output for the starter's markup, committed as
`nexy/modules/cli/templates/_partials/vanilla.css`. Run this script after changing the starter
markup or `globale.css.jinja2`, then commit the result:

    python scripts/build_vanilla_css.py

It needs Node.js and a network connection (it installs the Tailwind CLI in a temporary folder).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "nexy" / "modules" / "cli" / "templates"
OUTPUT = TEMPLATES / "_partials" / "vanilla.css"
TAILWIND_VERSION = "4.3.3"
# The variables of :root and .dark come from the project's own stylesheet header.
HEADER = re.compile(r"^:root \{.*?^\}\n\n\.dark \{.*?^\}\n", re.DOTALL | re.MULTILINE)


def render_tailwind_stylesheet() -> str:
    environment = Environment(loader=FileSystemLoader(TEMPLATES / "_shared" / "web"))
    template = environment.get_template("globale.css.jinja2")
    # The starter classes are plain CSS that every style includes itself: only Tailwind's own
    # reset and the utilities the project may use belong in this file.
    return template.render(style="tailwind", client_framework="react", starter=False)


def compile_css(source: str) -> str:
    npm, npx = shutil.which("npm"), shutil.which("npx")
    if npm is None or npx is None:
        raise SystemExit("npm not found: install Node.js")
    with tempfile.TemporaryDirectory() as folder:
        work = Path(folder)
        (work / "input.css").write_text(f'@source "{TEMPLATES.as_posix()}";\n{source}', "utf-8")
        packages = [f"tailwindcss@{TAILWIND_VERSION}", f"@tailwindcss/cli@{TAILWIND_VERSION}"]
        subprocess.run(
            [npm, "install", "--silent", "--no-audit", "--no-fund", *packages], cwd=work, check=True
        )  # noqa: S603
        command = [npx, "--no-install", "tailwindcss", "-i", "input.css", "-o", "output.css"]
        subprocess.run(command, cwd=work, check=True)  # noqa: S603
        return (work / "output.css").read_text("utf-8")


def main() -> int:
    source = HEADER.sub("", render_tailwind_stylesheet())
    css = compile_css(source)
    if "{{" in css or "{%" in css:
        raise SystemExit("the compiled CSS contains template syntax")
    OUTPUT.write_text(css, "utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(css) // 1000} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
