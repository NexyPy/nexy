"""The Vue build imports only what a Vue project declares, so it works under pnpm too (#595).

pnpm links a project's own dependencies into node_modules and nothing else: `@vue/*` packages,
dependencies of `vue`, cannot be imported from the project. `vue` exports what they hold.
"""

import re
from pathlib import Path

import nexy

SCRIPT = Path(nexy.__file__).parent / "modules" / "frontend" / "scripts" / "ssg.vue.ts"


def test_the_vue_build_imports_no_package_a_vue_project_does_not_declare():
    imported = re.findall(r"import\(\s*['\"]([^'\"]+)['\"]\s*\)", SCRIPT.read_text("utf-8"))
    assert [name for name in imported if name.startswith("@vue/")] == []
