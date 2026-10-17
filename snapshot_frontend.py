"""Snapshot harness: run FrontendGenerator on a scaffolded project and save outputs.

Usage: python snapshot.py <repo_root> <output_dir>
"""

import os
import sys
import tempfile
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()

sys.path.insert(0, str(REPO))

tmp = Path(tempfile.mkdtemp(prefix="nexy_snap_"))
routes = tmp / "src" / "routes"
routes.mkdir(parents=True)
(routes / "index.tsx").write_text(
    "export default function Home() { return null }", encoding="utf-8"
)
(routes / "index.nexy").write_text("---\n---\n<div>Home</div>", encoding="utf-8")
(routes / "about.md").write_text("# About", encoding="utf-8")
blog = routes / "blog"
blog.mkdir()
(blog / "index.tsx").write_text("export default function Blog() { return null }", encoding="utf-8")
(blog / "[slug].tsx").write_text("export default function Post() { return null }", encoding="utf-8")
(blog / "layout.tsx").write_text(
    "export default function L({children}) { return children }", encoding="utf-8"
)
(tmp / "src" / "components").mkdir(parents=True)
(tmp / "src" / "components" / "Btn.tsx").write_text(
    "export default function Btn() { return null }", encoding="utf-8"
)
(tmp / "nexyconfig.py").write_text(
    "from nexy.core.models import NexyConfigModel\n"
    "from nexy.frontend import react\n"
    "\n"
    "class NexyConfig(NexyConfigModel):\n"
    "    useFF = react()\n"
    "    excludeDirs = ['templates', 'docs']\n",
    encoding="utf-8",
)

os.chdir(tmp)
sys.path.insert(0, str(tmp))

from nexy.frontend import FrontendGenerator  # noqa: E402

FrontendGenerator().generate(ssg=True)

OUT.mkdir(parents=True, exist_ok=True)
root = tmp / "__nexy__"
count = 0
for p in sorted(root.rglob("*")):
    if p.is_file():
        rel = p.relative_to(root)
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(p.read_bytes())
        count += 1

sys.stdout.write(f"snapshot: {count} files -> {OUT}\n")
sys.stdout.write(f"temp project: {tmp}\n")