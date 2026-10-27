"""Render a .nexy component in a test, the way a page would, without a server.

    from nexy.testing import render

    def test_button_shows_its_label():
        assert "Save" in render("src/components/button.nexy", label="Save")

Run pytest from the project root: the compiled files go to ``__nexy__/`` there, like `nx dev`.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from nexy.core.config import Config
from nexy.modules.compiler import Compiler, default_output


def _compiled_module(component: Path) -> Path:
    """Compile the component and everything it imports; the Python file that was written."""
    Compiler().compile_with_deps(str(component))
    return Path(default_output(str(component))).with_suffix(".py")


def _component_name(module: Path) -> str:
    """The component is the one function a compiled module defines at its top level."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return node.name
    raise LookupError(f"{module} defines no component")


def _forget_compiled_modules() -> None:
    """Compiled modules are cached by name: drop them so an edited component is read again."""
    prefix = Config.NAMESPACE.strip("/")
    for name in [name for name in sys.modules if name == prefix or name.startswith(f"{prefix}.")]:
        del sys.modules[name]


def _load(module: Path) -> ModuleType:
    root = str(Path.cwd())
    if root not in sys.path:
        sys.path.insert(0, root)
    _forget_compiled_modules()
    spec = importlib.util.spec_from_file_location(f"_nexy_test_{module.stem}", module)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module}")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def render(component: str | Path, /, **props: Any) -> str:
    """The HTML of a .nexy component for these props; ``children=`` fills its slot."""
    path = Path(component)
    if path.suffix != ".nexy" or not path.is_file():
        raise FileNotFoundError(f"'{component}' is not a .nexy component")
    module = _compiled_module(path)
    return str(getattr(_load(module), _component_name(module))(**props))


__all__ = ["render"]
