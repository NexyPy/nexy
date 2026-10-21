import ast
from pathlib import Path

import nexy

NEXY_ROOT = Path(nexy.__file__).resolve().parent

GOOGLE_SECTIONS = ("Args:", "Returns:", "Raises:", "Attributes:")

# Anti-regression floors, measured with a single ast.walk pass (no double counting)
# on 2026-10-19: 365 public APIs (276 functions + 89 classes), 145 documented,
# 0 Google style. Raised after the media components/errors/hooks batch (160/15),
# then after the exported-surface batch: core/models.py, template.py, vite.py,
# form.py - now 176 documented, 27 Google style. Raise these floors as batches
# are written - never lower them.
BASELINE_WITH_DOCSTRING = 176
BASELINE_GOOGLE_SECTIONS = 27


def _count_public_api_docstrings() -> tuple[int, int, int]:
    """Return (public_apis, with_docstring, with_google_sections) over nexy/**.py."""
    public_apis = with_docstring = with_google = 0
    for path in sorted(NEXY_ROOT.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            is_def = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            if not (is_def or isinstance(node, ast.ClassDef)):
                continue
            if node.name.startswith("_"):
                continue
            if is_def:
                public_apis += 1
            else:
                public_apis += 1
            doc = ast.get_docstring(node)
            if not doc:
                continue
            with_docstring += 1
            if any(section in doc for section in GOOGLE_SECTIONS):
                with_google += 1
    return public_apis, with_docstring, with_google


class TestDocstringAntiRegression:
    def test_public_api_docstrings_never_shrink(self) -> None:
        _, with_docstring, _ = _count_public_api_docstrings()
        assert (
            with_docstring >= BASELINE_WITH_DOCSTRING
        ), f"Public API docstrings dropped: {with_docstring} < floor {BASELINE_WITH_DOCSTRING}"

    def test_google_style_sections_never_shrink(self) -> None:
        _, _, with_google = _count_public_api_docstrings()
        assert (
            with_google >= BASELINE_GOOGLE_SECTIONS
        ), f"Google-style docstrings dropped: {with_google} < floor {BASELINE_GOOGLE_SECTIONS}"
